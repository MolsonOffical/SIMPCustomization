import uuid
from collections import Counter
from datetime import timedelta

from django.core.cache import cache
from django.db.models import Count, Exists, F, Min, OuterRef, Q
from django.utils import timezone

from .models import OrderItem, ShoesVariant, Shoes, ShoeView

CONFIRMED_STATUSES = ["paid", "processing", "shipped", "delivered"]

PURCHASE_WEIGHT = 5
VIEW_WEIGHT = 1


def _in_stock(qs):
    has_stock = ShoesVariant.objects.filter(shoe=OuterRef("pk"), stock_quantity__gt=0)
    return qs.annotate(_in_stock=Exists(has_stock)).filter(_in_stock=True)


class ShoeRecommendationEngine:
    def __init__(self, user=None, visitor_id=None, cache_timeout=300, decay_days=90):
        self.user = user if user and getattr(user, "is_authenticated", False) else None
        self.visitor_id = visitor_id
        self.cache_timeout = cache_timeout
        self.decay_days = decay_days

    def get_cache_key(self, prefix):
        if self.user:
            return f"rec_{prefix}_user_{self.user.id}"
        elif self.visitor_id:
            return f"rec_{prefix}_visitor_{self.visitor_id}"
        return f"rec_{prefix}_anonymous"

    def invalidate_cache(self):
        cache.delete(self.get_cache_key("weights"))

    def log_view(self, shoe, dedupe_minutes=30):
        if not (self.user or self.visitor_id):
            return None

        identity = {"user": self.user} if self.user else {"visitor_id": self.visitor_id}

        if dedupe_minutes:
            cutoff = timezone.now() - timedelta(minutes=dedupe_minutes)
            if ShoeView.objects.filter(shoe=shoe, created_at__gte=cutoff, **identity).exists():
                return None

        return ShoeView.objects.create(shoe=shoe, **identity)

    def get_user_interactions(self):
        interacted = set()

        if self.user:
            purchased_ids = OrderItem.objects.filter(
                order__user=self.user,
                order__status__in=CONFIRMED_STATUSES,
                variant__isnull=False,  # FIX: customized/patterned orders have no variant/shoe link
            ).values_list("variant__shoe_id", flat=True).distinct()
            interacted.update(purchased_ids)

            viewed_ids = ShoeView.objects.filter(user=self.user).values_list(
                "shoe_id", flat=True
            ).distinct()
            interacted.update(viewed_ids)

        elif self.visitor_id:
            viewed_ids = ShoeView.objects.filter(visitor_id=self.visitor_id).values_list(
                "shoe_id", flat=True
            ).distinct()
            interacted.update(viewed_ids)

        return list(interacted)

    def _calculate_weights(self):
        category_weights = Counter()
        brand_weights = Counter()
        total_weight = 0.0

        def add_weight(shoe, base_weight, interaction_date):
            days_ago = max(0, (timezone.now() - interaction_date).days)
            decay_factor = max(0.3, 1 - (days_ago / self.decay_days))
            weight = base_weight * decay_factor

            if shoe.category_id:
                category_weights[shoe.category_id] += weight
            if shoe.brand_id:
                brand_weights[shoe.brand_id] += weight
            return weight

        if self.user:
            order_items = OrderItem.objects.filter(
                order__user=self.user,
                order__status__in=CONFIRMED_STATUSES,
                variant__isnull=False,  
            ).select_related("variant__shoe__category", "variant__shoe__brand", "order")

            seen_purchases = set()
            for item in order_items:
                shoe = item.variant.shoe
                key = (shoe.id, item.order_id)
                if key in seen_purchases:
                    continue
                seen_purchases.add(key)
                total_weight += add_weight(shoe, PURCHASE_WEIGHT, item.order.created_at)

            views = ShoeView.objects.filter(user=self.user).select_related(
                "shoe__category", "shoe__brand"
            ).order_by("-created_at")

            seen_views = set()
            for view in views:
                if view.shoe_id in seen_views:
                    continue
                seen_views.add(view.shoe_id)
                total_weight += add_weight(view.shoe, VIEW_WEIGHT, view.created_at)

        elif self.visitor_id:
            views = ShoeView.objects.filter(visitor_id=self.visitor_id).select_related(
                "shoe__category", "shoe__brand"
            ).order_by("-created_at")

            seen_views = set()
            for view in views:
                if view.shoe_id in seen_views:
                    continue
                seen_views.add(view.shoe_id)
                total_weight += add_weight(view.shoe, VIEW_WEIGHT, view.created_at)

        if total_weight > 0:
            norm = 1.0 / total_weight
            for cat_id in list(category_weights.keys()):
                category_weights[cat_id] *= norm
            for brand_id in list(brand_weights.keys()):
                brand_weights[brand_id] *= norm

        return category_weights, brand_weights

    def get_weighted_preferences(self, use_cache=True):
        cache_key = self.get_cache_key("weights")
        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

        weights = self._calculate_weights()

        if use_cache:
            cache.set(cache_key, weights, self.cache_timeout)

        return weights

    def calculate_similarity_score(self, shoe, category_weights, brand_weights):
        score = 0.0
        if shoe.category_id:
            score += category_weights.get(shoe.category_id, 0) * 1.5
        if shoe.brand_id:
            score += brand_weights.get(shoe.brand_id, 0)

        days_old = (timezone.now() - shoe.created_at).days
        if days_old <= 14:
            score += (14 - days_old) * 0.05 

        return score

    def _popular_shoes(self, limit, exclude_ids=None):
        qs = _in_stock(Shoes.objects.select_related("category", "brand"))
        if exclude_ids:
            qs = qs.exclude(id__in=exclude_ids)

        month_ago = timezone.now() - timedelta(days=30)
        recent_qs = qs.filter(created_at__gte=month_ago)

        if recent_qs.exists():
            recent_popular = recent_qs.annotate(
                min_price=Min("variants__price"),
                purchase_count=Count(
                    "variants__order_items",
                    filter=Q(variants__order_items__order__status__in=CONFIRMED_STATUSES),
                    distinct=True,
                ),
                view_count=Count("shoe_views", distinct=True),
            ).annotate(
                engagement=F("purchase_count") * 5 + F("view_count")
            ).order_by("-engagement", "-created_at")

            recent_popular = list(recent_popular[:limit])
            if len(recent_popular) >= limit:
                return recent_popular

        fallback = qs.annotate(
            min_price=Min("variants__price"),
            purchase_count=Count(
                "variants__order_items",
                filter=Q(variants__order_items__order__status__in=CONFIRMED_STATUSES),
                distinct=True,
            ),
        ).order_by("-purchase_count", "-created_at")

        return list(fallback[:limit])

    def _ensure_diversity(self, scored_shoes, limit, max_per_brand=3):
        final = []
        brand_counts = Counter()

        for shoe, score in scored_shoes:
            if len(final) >= limit:
                break
            if shoe.brand_id and brand_counts[shoe.brand_id] >= max_per_brand:
                continue
            final.append(shoe)
            if shoe.brand_id:
                brand_counts[shoe.brand_id] += 1

        if len(final) < limit:
            already_ids = {s.id for s in final}
            remaining = [s for s, _ in scored_shoes if s.id not in already_ids]
            final.extend(remaining[: limit - len(final)])

        return final

    def get_recommendations(self, limit=8, exclude_interacted=True):
        interacted_ids = self.get_user_interactions() if exclude_interacted else []

        if not interacted_ids:
            return self._popular_shoes(limit=limit)

        category_weights, brand_weights = self.get_weighted_preferences()

        if not category_weights and not brand_weights:
            return self._popular_shoes(limit=limit, exclude_ids=interacted_ids)

        top_categories = [cat_id for cat_id, _ in category_weights.most_common(5)]
        top_brands = [brand_id for brand_id, _ in brand_weights.most_common(5)]

        candidate_q = Q()
        if top_categories:
            candidate_q |= Q(category_id__in=top_categories)
        if top_brands:
            candidate_q |= Q(brand_id__in=top_brands)

        candidates = _in_stock(
            Shoes.objects.exclude(id__in=interacted_ids)
            .filter(candidate_q)
            .select_related("category", "brand")
        ).annotate(min_price=Min("variants__price")).distinct()

        scored = []
        for shoe in candidates:
            score = self.calculate_similarity_score(shoe, category_weights, brand_weights)
            if score > 0:
                scored.append((shoe, score))

        scored.sort(key=lambda pair: pair[1], reverse=True)

        if len(scored) > limit:
            recommended = self._ensure_diversity(scored, limit)
        else:
            recommended = [s for s, _ in scored[:limit]]

        if len(recommended) < limit:
            needed = limit - len(recommended)
            exclude_ids = [s.id for s in recommended] + interacted_ids
            recommended.extend(self._popular_shoes(limit=needed, exclude_ids=exclude_ids))

        return recommended

    def get_similar_shoes(self, shoe, limit=4):
        if not shoe.brand_id:
            return []
        qs = _in_stock(
            Shoes.objects.exclude(id=shoe.id).filter(brand_id=shoe.brand_id).select_related("category", "brand")
            ).annotate(min_price=Min("variants__price")).distinct()

        scored = []
        for s in qs:
            score = 2.0  # same-brand match

            days_old = (timezone.now() - s.created_at).days
            if days_old <= 30:
                score += max(0, (30 - days_old) * 0.05)

            scored.append((s, score))
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [s for s, _ in scored[:limit]]


def get_recommendation_engine(request):
    user = getattr(request, "user", None)
    visitor_id = None

    if hasattr(request, "session"):
        visitor_id = request.session.get("visitor_id")
        if not visitor_id:
            visitor_id = uuid.uuid4().hex
            request.session["visitor_id"] = visitor_id

    return ShoeRecommendationEngine(user=user, visitor_id=visitor_id)