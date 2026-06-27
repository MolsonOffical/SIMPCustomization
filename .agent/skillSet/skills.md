# SIMP — Agent Skillset Reference

**Project:** Shoe Identity & Modification Platform  
**Stack:** Django 6.0.6 · Python 3.12 · SQLite3 → PostgreSQL · Vanilla JS · Django Templates  
**Purpose:** This document defines the complete skill set required for an AI agent to build, extend, and maintain the SIMP platform end-to-end. Skills are grouped by discipline: Backend, Frontend, and Database (DBA).

---

## 1. Backend Skills

### 1.1 Django Core

| Skill | Details |
|-------|---------|
| Project & app structure | Understand Django's `project/app` separation; know when to create new apps (e.g., `catalog`, `orders`, `payments`, `blog`) vs. extending existing ones |
| Settings management | Manage `settings.py` for dev/staging/prod environments; use `python-decouple` or `django-environ` for secrets; configure `INSTALLED_APPS`, `MIDDLEWARE`, `TEMPLATES`, `STATIC_ROOT`, `MEDIA_ROOT` |
| URL routing | Write `urlpatterns` with `path()` and `include()`; use namespaces (`app_name`) for multi-app projects |
| Class-based views (CBVs) | Use `View`, `TemplateView`, `ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`; override `get_queryset`, `get_context_data`, `form_valid` correctly |
| Function-based views (FBVs) | Use `@login_required`, `@permission_required`, `@require_POST` decorators; know when FBVs are cleaner than CBVs |
| Django admin | Register models with `ModelAdmin`; customize `list_display`, `search_fields`, `list_filter`, `readonly_fields`, `inlines`; add custom admin actions |
| Django messages framework | Use `messages.success/error/warning/info`; display messages in templates with proper styling |
| Django signals | Use `post_save`, `pre_delete` signals for side-effects (e.g., sending confirmation emails on order creation) |
| Middleware | Write custom middleware (e.g., to enforce `is_email_verified` before accessing protected pages) |
| Management commands | Write `manage.py` custom commands for seeding data, clearing expired OTPs, running scheduled jobs |

---

### 1.2 Authentication & Authorization

| Skill | Details |
|-------|---------|
| Custom user model | Extend `AbstractUser` with extra fields (`age`, `gender`, `phone_number`, `profile`, `banner`, `is_email_verified`); always set `AUTH_USER_MODEL` before first migration |
| Django auth views | Use `LoginView`, `LogoutView`, `PasswordChangeView`, `PasswordResetView` as base classes; override templates and success URLs |
| OTP-based email verification | Generate cryptographically safe 6-digit codes; store with expiry (`EmailOTP` model); delete on use or expiry; send via SMTP |
| Session management | Use `request.session` for short-lived state (e.g., `pending_user_id`); set expiry and clean up after verification |
| Permission system | Use `user.is_staff`, `user.is_superuser` guards; block staff from public login endpoint; protect admin-only views |
| Password security | Apply Django's built-in validators (`MinimumLengthValidator`, `CommonPasswordValidator`); optionally add `zxcvbn` for strength scoring |
| OAuth / Social auth | Integrate `django-allauth` for future Google/Facebook login if needed |
| Login-required protection | Use `LoginRequiredMixin` on CBVs or `@login_required` on FBVs; redirect unauthenticated users to login with `next` parameter preserved |

---

### 1.3 Forms & Validation

| Skill | Details |
|-------|---------|
| ModelForms | Use `ModelForm` with explicit `Meta.fields`; override `clean_<field>()` for custom rules |
| Form inheritance | Extend `UserCreationForm`, `AuthenticationForm` correctly without breaking parent `save()` logic |
| Custom validators | Write reusable `validators.py` functions (Nepal phone regex, alphanumeric username, image size/type); attach via `field.validators = [...]` |
| File upload forms | Handle `request.FILES`; validate MIME type, file size; use `enctype="multipart/form-data"` |
| Form rendering | Apply CSS classes dynamically in `__init__` via `self.fields[f].widget.attrs`; add `placeholder`, `autocomplete` attributes |
| Formsets | Use `inlineformset_factory` for multi-item forms (e.g., order line items, multiple images) |
| CSRF protection | Never disable `CsrfViewMiddleware`; use `{% csrf_token %}` in every POST form; use `csrf_exempt` only on verified webhook endpoints |

---

### 1.4 Email & Notifications

| Skill | Details |
|-------|---------|
| SMTP configuration | Configure `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS/SSL`, `EMAIL_HOST_USER/PASSWORD` in settings |
| Custom email backends | Write a subclass of `EmailBackend` to override SSL context (as in `CustomEmailBackend`) for dev; use standard backend in production |
| HTML + plain-text emails | Send multipart emails using `EmailMultiAlternatives`; always include a plain-text fallback |
| Transactional email templates | Create reusable Django template-based email bodies for OTP, order confirmation, password reset |
| Email in production | Integrate SendGrid, Mailgun, or AWS SES via their Django packages for production delivery |

---

### 1.5 E-commerce Backend (Planned)

| Skill | Details |
|-------|---------|
| Product catalog models | Design `Category`, `Product`, `ProductImage`, `SizeVariant`, `ColorOption` models with proper FKs and M2M relationships |
| Shoe customization models | Design `CustomizationOrder` with JSON or normalized fields for color, pattern, artwork, size |
| Cart & sessions | Implement session-based cart (anonymous) and DB-backed cart (authenticated); merge on login |
| Order lifecycle | Model `Order` with statuses (`PENDING → CONFIRMED → PROCESSING → SHIPPED → DELIVERED → CANCELLED`); use FSM or simple CharField with choices |
| Payment gateway integration | Integrate eSewa and Khalti APIs using `requests`; verify payment signatures server-side; never trust client-reported amounts |
| Inventory management | Track stock per SKU; decrement on order confirmation; raise `OutOfStock` errors gracefully |
| Pricing in NPR | Store prices as `DecimalField(max_digits=10, decimal_places=2)`; format as `Rs. X,XXX` in templates |
| Webhooks | Handle payment provider webhooks with `@csrf_exempt` + HMAC signature verification |

---

### 1.6 REST API (Future)

| Skill | Details |
|-------|---------|
| Django REST Framework | Serializers, ViewSets, Routers, `APIView`; use `ModelSerializer` for standard CRUD |
| Authentication | Token auth or JWT (`djangorestframework-simplejwt`) for mobile/SPA clients |
| Permissions | `IsAuthenticated`, `IsAdminUser`, custom `BasePermission` classes |
| Pagination | `PageNumberPagination` or `CursorPagination` for large lists |
| Filtering | `django-filter` integration; search and ordering via `SearchFilter`, `OrderingFilter` |
| Throttling | Apply rate limits on OTP endpoints and payment initiation routes |

---

### 1.7 File & Media Handling

| Skill | Details |
|-------|---------|
| Pillow | Resize/compress images on upload using `PIL.Image`; generate thumbnails; validate dimensions |
| `ImageField` / `FileField` | Set `upload_to` callables (e.g., `upload_to='profile/%Y/%m/'`); override `save()` to delete old files |
| `MEDIA_URL` / `MEDIA_ROOT` | Serve media in dev via `django.views.static.serve`; use CDN or S3 in production |
| Artwork uploads | Accept PNG/SVG for shoe customization artwork; validate MIME type and max dimensions |
| Storage backends | Integrate `django-storages` + `boto3` for S3 (production static/media) |

---

### 1.8 Security

| Skill | Details |
|-------|---------|
| Django security checklist | Run `python manage.py check --deploy`; enable `SECURE_SSL_REDIRECT`, `HSTS`, `X_FRAME_OPTIONS`, `SECURE_CONTENT_TYPE_NOSNIFF` |
| Input sanitization | Never trust user input in queries; always use ORM (parameterized queries); avoid raw SQL unless absolutely necessary |
| Rate limiting | Use `django-ratelimit` on login, registration, OTP endpoints to prevent brute force |
| Environment secrets | Never commit `SECRET_KEY`, DB credentials, or SMTP passwords; use `.env` + `python-decouple` |
| XSS protection | Use `{{ var \| escape }}` or rely on Django's auto-escaping; mark safe only intentional HTML |
| SQL injection | ORM protects by default; audit any `raw()` or `extra()` usage carefully |

---

### 1.9 Testing (Backend)

| Skill | Details |
|-------|---------|
| `django.test.TestCase` | Write unit tests for models, forms, validators, and service functions |
| `Client` test client | Simulate GET/POST requests; assert response status codes, redirects, context data |
| Factory Boy / Faker | Generate realistic test data for users, products, orders |
| Mocking | Use `unittest.mock.patch` to mock SMTP sending, payment API calls during tests |
| Coverage | Run `coverage.py`; aim for ≥80% on `services.py`, `validators.py`, `models.py` |

---

## 2. Frontend Skills

### 2.1 Django Templates

| Skill | Details |
|-------|---------|
| Template inheritance | Use `{% extends "layout.html" %}` + `{% block content %}` correctly; avoid duplicate footer by keeping a single footer in `layout.html` and removing the inline one from `index.html` |
| Template tags & filters | Use `{% url %}`, `{% static %}`, `{% if %}`, `{% for %}`, `{% with %}`; apply filters like `\| date`, `\| truncatechars`, `\| floatformat:0` |
| Context processors | Pass global data (cart count, user, categories) via `context_processors` rather than in every view |
| Includes | Use `{% include "partials/_navbar.html" %}` for reusable sub-templates |
| Custom template tags | Write `templatetags/` for complex rendering logic (e.g., star ratings, price formatting in NPR) |
| Static files | Use `{% load static %}` + `{% static 'path' %}`; never hardcode `/static/` paths |
| Escaping | Trust Django's auto-escaping; only use `\| safe` on content you control (e.g., rich text from a trusted editor) |

---

### 2.2 CSS

| Skill | Details |
|-------|---------|
| Design tokens | Define a consistent token system in CSS custom properties: `--color-primary: #1a7a4a`, `--color-accent: #2ea865`, `--color-dark: #111`, `--font-display: 'Barlow Condensed'`, `--font-body: 'Inter'` |
| Layout systems | Use CSS Grid for page-level layouts (hero split, product grid, footer columns); Flexbox for component-level alignment (nav, pills, badges) |
| Responsive design | Mobile-first breakpoints: `480px` (single-column), `768px` (tablet adjustments), `1024px` (desktop). Hide/stack columns with `grid-template-columns: 1fr` at mobile |
| Component scoping | Organize per-page CSS files (`home.css`, `register.css`, `login.css`); share resets and tokens in a `base.css` loaded globally |
| Navbar | Sticky white navbar with scroll shadow; mobile hamburger menu using checkbox hack or JS toggle; animated category dropdown |
| Forms | Styled `form-control` inputs with focus rings, error states (red border + message), and success states; pill-style buttons |
| Accessibility | Visible `:focus-visible` rings on all interactive elements; sufficient color contrast (WCAG AA); `prefers-reduced-motion` media query on animations |
| Typography scale | Set a clear scale: `clamp()` for fluid display headings; consistent line heights; `font-weight` used intentionally (400 body, 600 labels, 700–800 headings) |
| Print / dark mode | Basic `prefers-color-scheme: dark` variables for future theme toggle |

---

### 2.3 JavaScript (Vanilla)

| Skill | Details |
|-------|---------|
| DOM manipulation | `querySelector`, `querySelectorAll`, `addEventListener`, `classList.add/remove/toggle` |
| Navbar dropdown | Mouseenter/mouseleave fade-in/out for category dropdown (`navbar.js`); keyboard `Escape` to close |
| Mobile menu | Toggle hamburger; trap focus inside open menu; close on outside click |
| OTP input UX | Auto-advance cursor to next digit box on input; support paste of full 6-digit code; aggregate digits into hidden `<input>` for POST; disable submit until 6 digits entered |
| Countdown timer | JS `setInterval` for 10-minute OTP expiry countdown; show/hide resend button when timer hits zero |
| FAQ accordion | Toggle `max-height` or `display` on answer panels; rotate arrow icon; close others on open |
| Form UX | Disable submit button on POST to prevent double-submission; show loading spinner; re-enable on error response |
| Image preview | `FileReader` API to show profile/banner preview before upload |
| Fetch / AJAX | Use `fetch()` with CSRF token for async actions (e.g., add to cart without page reload); handle JSON responses |
| Event delegation | Attach single listener on parent for dynamic lists (product cards, cart items) |

---

### 2.4 UI Components (To Build)

| Component | Skills Required |
|-----------|----------------|
| Navbar + mobile drawer | CSS sticky, JS toggle, ARIA `aria-expanded`, `role="navigation"` |
| Hero section | CSS Grid split, responsive stack, animated CTA button |
| Product card | Hover lift shadow, image aspect-ratio lock, price badge in NPR |
| Shoe customization UI | Canvas or SVG overlay for color/pattern preview; color picker widget; file drop zone for artwork |
| Cart sidebar / modal | Slide-in panel; quantity stepper; real-time subtotal via JS |
| Checkout form | Multi-step form with progress indicator; payment method selection (eSewa, Khalti, card) |
| OTP digit inputs | 6-box input with auto-advance, paste, countdown |
| Toast notifications | Fixed-position, auto-dismiss alerts for cart add, errors, success |
| FAQ accordion | Animated expand/collapse with `<details>` or custom JS |
| Image gallery | Lightbox for product photos; thumbnail strip |
| Star rating widget | CSS-only or JS-driven; half-star support for reviews |
| Pagination controls | Previous/Next + page numbers; active state |
| Admin-style dashboard | (Future) Order stats, recent activity — clean table layout |

---

### 2.5 Fonts & Icons

| Skill | Details |
|-------|---------|
| Google Fonts | Load `Inter` (body) and `Barlow Condensed` (display) via `<link>` in `layout.html`; subset with `&display=swap` |
| Font Awesome 6 | Use for nav icons, social links, arrows; load from CDN; prefer `<i class="fa-solid fa-...">` with `aria-hidden="true"` |
| Icon accessibility | Pair icon-only buttons with `aria-label`; never rely on icon alone for meaning |
| Custom SVG icons | Inline SVG for brand-critical icons (logo, shoe customizer tools) for full color/animation control |

---

### 2.6 Performance (Frontend)

| Skill | Details |
|-------|---------|
| Static file caching | Use `ManifestStaticFilesStorage` in production to cache-bust CSS/JS with content hashes |
| Image optimization | Compress uploads server-side with Pillow; serve WebP where supported; use `loading="lazy"` on below-fold images |
| CSS/JS minification | Use `django-compressor` or build step (Vite/Webpack) for production bundles |
| Critical CSS | Inline above-the-fold CSS for home page to eliminate render-blocking |

---

### 2.7 Accessibility & UX

| Skill | Details |
|-------|---------|
| Semantic HTML | Use `<main>`, `<nav>`, `<header>`, `<footer>`, `<article>`, `<section>`, `<aside>` correctly |
| ARIA attributes | `aria-label`, `aria-expanded`, `aria-describedby` (link error messages to inputs), `role` attributes |
| Keyboard navigation | All interactive elements reachable and operable via keyboard; logical tab order |
| Color contrast | Minimum 4.5:1 for body text; 3:1 for large text; test green accent `#1a7a4a` on white |
| Error handling UX | Per-field errors appear below the relevant input; never show only a generic "form invalid" message |
| Loading states | Disable buttons during async ops; show spinner; re-enable on completion |

---

## 3. Database Skills (DBA)

### 3.1 Django ORM Fundamentals

| Skill | Details |
|-------|---------|
| Model definition | `CharField`, `TextField`, `IntegerField`, `DecimalField`, `BooleanField`, `DateTimeField`, `ImageField`, `ForeignKey`, `ManyToManyField`, `OneToOneField` with correct `on_delete` policies |
| `Meta` options | `ordering`, `verbose_name`, `verbose_name_plural`, `unique_together`, `indexes`, `constraints` |
| Migrations | `makemigrations`, `migrate`, `showmigrations`, `sqlmigrate`; write data migrations with `RunPython` for seeding or transforming data |
| Querysets | `filter()`, `exclude()`, `get()`, `annotate()`, `aggregate()`, `select_related()`, `prefetch_related()`, `only()`, `defer()`, `values()`, `values_list()` |
| Transactions | Use `transaction.atomic()` for multi-step operations (e.g., create order + decrement stock atomically) |
| F and Q expressions | Use `F()` for atomic field updates (stock decrement); `Q()` for complex OR/AND filters |
| Custom managers | Write a `Manager` subclass for common filtered querysets (e.g., `Product.objects.active()`, `Order.objects.pending()`) |
| Model `save()` override | Use for side-effects (delete old images, auto-generate slugs, set defaults) — always call `super().save()` |

---

### 3.2 Schema Design

#### Current Tables (Implemented)

| Table | Key Fields | Notes |
|-------|-----------|-------|
| `account_customuser` | `id`, `username`, `email`, `age`, `gender`, `phone_number`, `profile`, `banner`, `is_email_verified`, `date_joined` | Extends `auth_user` via `AbstractUser` |
| `account_emailotp` | `id`, `user_id (FK)`, `otp`, `created_at`, `expires_at` | Deleted on use or expiry |

#### Planned Tables (To Design & Implement)

| Table | Key Fields | Notes |
|-------|-----------|-------|
| `catalog_category` | `id`, `name`, `slug`, `description`, `image`, `is_active` | Hierarchical optional (`parent_id FK self`) |
| `catalog_product` | `id`, `category_id`, `name`, `slug`, `description`, `base_price`, `is_active`, `created_at` | Canonical product record |
| `catalog_productimage` | `id`, `product_id`, `image`, `alt_text`, `is_primary`, `order` | Multiple images per product |
| `catalog_sizevariant` | `id`, `product_id`, `size_label`, `eu_size`, `uk_size`, `us_size`, `stock_qty` | Nepal market: EU/UK/US sizing |
| `catalog_coloroption` | `id`, `product_id`, `color_name`, `hex_code`, `stock_qty` | Per-color inventory |
| `customization_design` | `id`, `user_id`, `product_id`, `base_color`, `pattern`, `artwork`, `size`, `notes`, `created_at` | User's saved customization |
| `cart_cart` | `id`, `user_id (nullable)`, `session_key`, `created_at`, `updated_at` | Nullable user for anonymous cart |
| `cart_cartitem` | `id`, `cart_id`, `product_id`, `customization_id (nullable)`, `size_variant_id`, `quantity`, `unit_price` | Line item snapshot |
| `orders_order` | `id`, `user_id`, `status`, `subtotal`, `shipping_fee`, `total`, `payment_method`, `payment_status`, `created_at`, `updated_at` | NPR amounts as `DecimalField` |
| `orders_orderitem` | `id`, `order_id`, `product_id`, `customization_id (nullable)`, `size_label`, `quantity`, `unit_price` | Snapshot of price at purchase time |
| `orders_shippingaddress` | `id`, `order_id`, `full_name`, `phone`, `province`, `district`, `city`, `street_address`, `postal_code` | Nepal address structure |
| `payments_transaction` | `id`, `order_id`, `provider`, `provider_ref`, `amount`, `status`, `raw_response (JSON)`, `created_at` | eSewa / Khalti / card |
| `reviews_review` | `id`, `user_id`, `product_id`, `rating (1–5)`, `title`, `body`, `is_approved`, `created_at` | Moderated; not shown until approved |
| `blog_post` | `id`, `author_id`, `category_id`, `title`, `slug`, `content`, `cover_image`, `is_published`, `published_at` | Rich text body |
| `blog_category` | `id`, `name`, `slug` | Separate from product categories |

---

### 3.3 Migrations Best Practices

| Skill | Details |
|-------|---------|
| Squashing | Periodically squash old migrations with `squashmigrations` to keep history clean |
| Data migrations | Use `migrations.RunPython` to seed initial categories, sizes, or transform data between schema versions |
| Reversible migrations | Always implement `reverse_func` in `RunPython` or use `RunSQL` with reverse SQL |
| Migration conflicts | Resolve merge conflicts with `makemigrations --merge`; never manually edit generated migration files unless necessary |
| Zero-downtime migrations | Add columns as nullable first; backfill; then add `NOT NULL` in a separate migration |

---

### 3.4 Indexing & Performance

| Skill | Details |
|-------|---------|
| Django indexes | Add `db_index=True` on FK fields, `slug`, `status`, `is_active`, `created_at` when used in filters or ordering |
| Composite indexes | Use `Meta.indexes = [models.Index(fields=['status', 'created_at'])]` for multi-column queries |
| `select_related` | Use for ForeignKey / OneToOne to avoid N+1 queries (e.g., `Order.objects.select_related('user')`) |
| `prefetch_related` | Use for ManyToMany / reverse FK (e.g., `Product.objects.prefetch_related('images', 'size_variants')`) |
| `django-debug-toolbar` | Install in dev to inspect SQL queries per request; identify N+1 issues |
| Query optimization | Use `only()` / `defer()` to fetch only needed columns for list views |
| Pagination | Always paginate querysets on list views; never load entire `Product.objects.all()` into a template |

---

### 3.5 Database Configuration

| Skill | Details |
|-------|---------|
| SQLite3 (dev) | Default Django config; sufficient for local development; do not use in production |
| PostgreSQL (production) | Switch to `psycopg2-binary`; configure `DATABASES` with host, port, name, user, password from environment variables |
| Connection pooling | Use `django-db-pool` or PgBouncer in production to manage PostgreSQL connections |
| Backups | Schedule `pg_dump` daily; test restore procedure quarterly; store backups off-server (S3 / Backblaze) |
| Fixtures | Use `dumpdata` / `loaddata` for seeding dev/test environments with realistic data |
| `DATABASE_URL` | Use `dj-database-url` to parse a single `DATABASE_URL` env variable for Heroku / Railway / Render deployments |

---

### 3.6 Data Integrity & Constraints

| Skill | Details |
|-------|---------|
| `on_delete` policies | `CASCADE` for child records that shouldn't outlive parent (e.g., `CartItem → Cart`); `PROTECT` for records that must not be orphaned (e.g., `OrderItem → Product`); `SET_NULL` for optional FKs |
| `unique_together` / `UniqueConstraint` | Enforce `(user, product)` uniqueness on reviews; `(cart, product, size_variant)` on cart items |
| `CheckConstraint` | Enforce `rating BETWEEN 1 AND 5`; `quantity > 0`; `total >= 0` at the DB level |
| `DecimalField` precision | Use `DecimalField(max_digits=10, decimal_places=2)` for all NPR monetary values; never use `FloatField` for money |
| Soft deletes | Use `is_active = BooleanField(default=True)` instead of hard-deleting products/categories that have orders |
| Audit fields | Add `created_at = DateTimeField(auto_now_add=True)` and `updated_at = DateTimeField(auto_now=True)` to all major models |

---

### 3.7 OTP & Session Data Hygiene

| Skill | Details |
|-------|---------|
| OTP expiry | Store `expires_at` on `EmailOTP`; filter with `expires_at__gt=timezone.now()` on verification; delete expired records |
| Expired OTP cleanup | Write a management command `clean_expired_otps.py`; schedule with cron or Celery Beat |
| Session cleanup | Run `python manage.py clearsessions` periodically; configure `SESSION_COOKIE_AGE` |
| Anonymous cart cleanup | Periodically delete carts with no `user` and `created_at` older than 30 days |

---

### 3.8 Search & Filtering

| Skill | Details |
|-------|---------|
| ORM-based search | Use `Q(name__icontains=q) \| Q(description__icontains=q)` for simple search |
| PostgreSQL full-text search | Use `django.contrib.postgres` `SearchVector`, `SearchQuery`, `SearchRank` for relevance-ranked product search |
| `django-filter` | Integrate `FilterSet` for faceted filtering (category, price range, size, color) on product list pages |
| Slug-based URLs | Auto-generate slugs with `django-autoslug` or `slugify()` in `save()`; enforce uniqueness |

---

## 4. Cross-Cutting Skills

### 4.1 Deployment

| Skill | Details |
|-------|---------|
| `gunicorn` / `uvicorn` | Run Django with `gunicorn project_simp.wsgi` in production |
| `nginx` | Reverse proxy; serve static/media files directly; SSL termination |
| Environment variables | All secrets in `.env`; loaded via `python-decouple`; never in `settings.py` |
| `collectstatic` | Run before deployment; configure `STATIC_ROOT`; use `WhiteNoise` or nginx to serve |
| Health check endpoint | Expose `/health/` returning `200 OK` for load balancer / uptime monitor |

---

### 4.2 Celery (Async Tasks)

| Skill | Details |
|-------|---------|
| Task queue setup | Configure `celery` + Redis broker for async email sending, OTP delivery, payment verification |
| Periodic tasks | Use `celery-beat` for scheduled jobs: OTP cleanup, order status sync, email digests |
| Retry logic | Use `task.retry(countdown=60, max_retries=3)` for transient SMTP / payment API failures |

---

### 4.3 Nepal-Specific Requirements

| Skill | Details |
|-------|---------|
| Phone validation | Nepal mobile: `^(\+977)?(98\|97\|91)\d{8}$`; strip `+977` prefix before storing |
| Currency | All prices in NPR (Rs.); format as `Rs. 1,200` in templates using custom template filter |
| Payment gateways | eSewa and Khalti official Python SDKs / REST APIs; test in sandbox before production |
| Address structure | Nepal address: Province → District → Municipality/City → Ward/Street |
| Time zone | `TIME_ZONE = 'Asia/Kathmandu'` in `settings.py`; use `timezone.now()` always (never `datetime.now()`) |
| Locale | `LANGUAGE_CODE = 'en-us'` acceptable; optionally add Nepali (`ne`) language support with `django.utils.translation` |

---

*Last updated: June 26, 2026 · SIMP v0.1 (Early Development)*