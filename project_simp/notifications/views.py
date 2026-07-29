from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views import View

from .models import Notification

PAGE_SIZE = 10


def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


class NotificationListView(LoginRequiredMixin, View):
    login_url = 'account:login'

    def get(self, request):
        filter_param = request.GET.get('filter', 'all')
        qs = Notification.objects.filter(user=request.user)

        if filter_param == 'unread':
            qs = qs.filter(is_read=False)
        elif filter_param == 'read':
            qs = qs.filter(is_read=True)

        paginator = Paginator(qs, PAGE_SIZE)
        page_obj = paginator.get_page(request.GET.get('page', 1))

        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        total_count = Notification.objects.filter(user=request.user).count()

        context = {
            'page_obj': page_obj,
            'active_filter': filter_param,
            'unread_count': unread_count,
            'total_count': total_count,
        }

        if _is_ajax(request):
            html = render_to_string('notifications/_notification_items.html', context, request=request)
            return JsonResponse({
                'html': html,
                'unread_count': unread_count,
                'total_count': total_count,
            })

        return render(request, 'notifications/notification_list.html', context)


class NotificationDetailView(LoginRequiredMixin, View):
    login_url = 'account:login'

    def get(self, request, pk):
        notification = get_object_or_404(
            Notification.objects.select_related('order'),
            pk=pk,
            user=request.user,
        )
        if not notification.is_read:
            notification.mark_as_read()

        order_items = []
        if notification.order:
            order_items = notification.order.items.select_related(
                'variant__shoe', 'variant__color', 'variant__size'
            ).all()

        return render(request, 'notifications/notification_detail.html', {
            'notification': notification,
            'order_items': order_items,
        })


class MarkAsReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.mark_as_read()
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        if _is_ajax(request):
            return JsonResponse({'success': True, 'unread_count': unread_count})
        return redirect('notifications:list')


class ToggleReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        if notification.is_read:
            notification.mark_as_unread()
        else:
            notification.mark_as_read()
        if _is_ajax(request):
            return JsonResponse({'success': True, 'is_read': notification.is_read})
        return redirect('notifications:detail', pk=pk)


class MarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
        if _is_ajax(request):
            return JsonResponse({'success': True})
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications:list')


class DeleteNotificationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.delete()
        if _is_ajax(request):
            return JsonResponse({'success': True})
        messages.success(request, 'Notification deleted.')
        return redirect('notifications:list')


class UnreadCountView(LoginRequiredMixin, View):
    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({'unread_count': count})