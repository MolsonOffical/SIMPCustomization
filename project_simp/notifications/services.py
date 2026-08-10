from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from .models import Notification, NotificationType

User = get_user_model()


def _send_email_safely(subject, text_message, html_message, recipient_email):
    try:
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"[Notification Email Error] Failed to send to {recipient_email}: {e}")
        return False


def notify_purchase_success(order):
    user = order.user
    if user is None:
        return None

    notification = Notification.objects.create(
        user=user,
        notification_type=NotificationType.PURCHASE,
        title="Purchase Successful",
        message=(
            f"Your order {order.order_id} has been placed successfully. "
            f"Please wait while we prepare it for delivery."
        ),
        order=order,
    )

    _send_purchase_email(user, order)

    return notification


def _order_items_for_email(order):
    return order.items.select_related('variant__shoe', 'variant__color', 'variant__size').all()


def _item_email_name(item):
    """Item display name for order emails.

    Catalog items have a `variant` (shoe/color/size picked from stock).
    Customizer items have `variant=None` and store `pattern` instead —
    this mirrors the variant/pattern branch already used in
    shoes/views.py's `_serialize_item`.
    """
    if item.variant_id:
        return item.variant.shoe.name
    return getattr(item, 'pattern_display_name', None) or item.pattern.replace('-', ' ').title()


def _item_email_detail(item):
    """Item subtitle (color/size for catalog items, size only for custom)."""
    if item.variant_id:
        return f"{item.variant.color.name} · Size {item.variant.size.size_value}"
    return f"Custom design · Size {item.size}"


def _build_items_table_html(order):
    rows = []
    for item in _order_items_for_email(order):
        rows.append(f"""
            <tr>
              <td style="padding:10px 8px;border-bottom:1px solid #e5e7eb;font-size:13px;color:#374151;text-align:left;">
                {_item_email_name(item)}<br>
                <span style="color:#9ca3af;font-size:11px;">{_item_email_detail(item)}</span>
              </td>
              <td style="padding:10px 8px;border-bottom:1px solid #e5e7eb;font-size:13px;color:#374151;text-align:center;">{item.quantity}</td>
              <td style="padding:10px 8px;border-bottom:1px solid #e5e7eb;font-size:13px;color:#374151;text-align:right;">Rs. {item.price:.2f}</td>
              <td style="padding:10px 8px;border-bottom:1px solid #e5e7eb;font-size:13px;color:#111827;font-weight:600;text-align:right;">Rs. {item.subtotal():.2f}</td>
            </tr>""")
    rows_html = ''.join(rows)
    return f"""
      <table style="width:100%;border-collapse:collapse;margin:20px 0 4px;">
        <thead>
          <tr style="background:#f5f3ff;">
            <th style="padding:9px 8px;text-align:left;font-size:11px;letter-spacing:0.4px;text-transform:uppercase;color:#4f46e5;">Item</th>
            <th style="padding:9px 8px;text-align:center;font-size:11px;letter-spacing:0.4px;text-transform:uppercase;color:#4f46e5;">Qty</th>
            <th style="padding:9px 8px;text-align:right;font-size:11px;letter-spacing:0.4px;text-transform:uppercase;color:#4f46e5;">Price</th>
            <th style="padding:9px 8px;text-align:right;font-size:11px;letter-spacing:0.4px;text-transform:uppercase;color:#4f46e5;">Subtotal</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
        <tfoot>
          <tr>
            <td colspan="3" style="padding:14px 8px 0;text-align:right;font-size:14px;font-weight:700;color:#111827;">Overall Total</td>
            <td style="padding:14px 8px 0;text-align:right;font-size:14px;font-weight:700;color:#4f46e5;">Rs. {order.total_amount:.2f}</td>
          </tr>
        </tfoot>
      </table>"""


def _build_items_lines_text(order):
    lines = []
    for item in _order_items_for_email(order):
        lines.append(
            f"  - {_item_email_name(item)} ({_item_email_detail(item)}) "
            f"x{item.quantity} @ Rs. {item.price:.2f} = Rs. {item.subtotal():.2f}"
        )
    return '\n'.join(lines) if lines else "  (no items found on this order)"


def _send_purchase_email(user, order):
    subject = "Your Purchase Was Successful"

    text_message = f"""
Hi {user.first_name or user.username},

Thank you for your purchase! Your order ({order.order_id}) has been received successfully.

{_build_items_lines_text(order)}

Overall Total: Rs. {order.total_amount:.2f}

Please wait for your delivery to reach you. We'll notify you once it arrives.

— The SIMP Team
"""

    items_table_html = _build_items_table_html(order)

    html_message = f"""
<!DOCTYPE html>
<html>
<body style="font-family: 'Segoe UI', Arial, sans-serif; background: #f4f4f8; margin: 0; padding: 40px 0;">
  <div style="max-width: 480px; margin: 0 auto; background: #fff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.08);">
    <div style="background: linear-gradient(135deg, #4f46e5, #7c3aed); padding: 36px 32px; text-align: center;">
      <h1 style="color: #fff; margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">Purchase Successful</h1>
      <p style="color: rgba(255,255,255,0.8); margin: 8px 0 0; font-size: 14px;">Thanks for shopping with SIMP</p>
    </div>
    <div style="padding: 40px 32px; text-align: center;">
      <p style="color: #6b7280; font-size: 15px; margin: 0 0 24px;">
        Hi <strong style="color:#111827;">{user.first_name or user.username}</strong>, your order has been received.
      </p>
      <div style="background: #f5f3ff; border: 2px dashed #a78bfa; border-radius: 12px; padding: 20px; display: inline-block; margin-bottom: 24px;">
        <p style="margin:0; color:#6d28d9; font-size:13px; letter-spacing: 0.5px; text-transform: uppercase;">Order ID</p>
        <p style="margin:4px 0 0; color:#4f46e5; font-size:20px; font-weight:800; letter-spacing:1px; font-family:'Courier New', monospace;">{order.order_id}</p>
      </div>

      {items_table_html}

      <p style="color: #4b5563; font-size: 14px; margin: 20px 0 0;">
        Please wait for your delivery to reach you. We'll let you know as soon as it's on its way.
      </p>
    </div>
    <div style="background: #f9fafb; padding: 20px 32px; text-align: center; border-top: 1px solid #e5e7eb;">
      <p style="color: #d1d5db; font-size: 12px; margin: 0;">This is an automated message, please do not reply.</p>
    </div>
  </div>
</body>
</html>
"""
    return _send_email_safely(subject, text_message, html_message, user.email)


def notify_delivery_success(order):
    user = order.user
    if user is None:
        return None

    notification = Notification.objects.create(
        user=user,
        notification_type=NotificationType.DELIVERY,
        title="Order Delivered",
        message=f"Your order {order.order_id} has been delivered successfully. Enjoy!",
        order=order,
    )
    _send_order_failed_email(user, order)
    return notification
    


def send_admin_broadcast(title, message):
    users = User.objects.filter(is_active=True, is_staff=False, is_superuser=False)
    notifications = [
        Notification(
            user=user,
            notification_type=NotificationType.ADMIN,
            title=title,
            message=message,
        )
        for user in users
    ]
    created = Notification.objects.bulk_create(notifications)
    return len(created)

def notify_order_failed(order):
    user = order.user
    if user is None:
        return None

    notification = Notification.objects.create(
        user=user,
        notification_type=NotificationType.FAILED,
        title="Order Failed",
        message=(
            f"Your order {order.order_id} could not be processed. "
            f"Please try again or contact support if this keeps happening."
        ),
        order=order,
    )

    _send_order_failed_email(user, order)

    return notification


def _send_order_failed_email(user, order):
    subject = "There Was a Problem With Your Order"

    text_message = f"""
Hi {user.first_name or user.username},

Unfortunately, we couldn't process your order ({order.order_id}).

This can happen due to a payment issue, an out-of-stock item, or a temporary system error. No charge should have been made, but please check your payment method to be sure.

You're welcome to try placing the order again. If the problem keeps happening, reach out to our support team and we'll help sort it out.

— The SIMP Team
"""

    html_message = f"""
<!DOCTYPE html>
<html>
<body style="font-family: 'Segoe UI', Arial, sans-serif; background: #f4f4f8; margin: 0; padding: 40px 0;">
  <div style="max-width: 480px; margin: 0 auto; background: #fff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.08);">
    <div style="background: linear-gradient(135deg, #dc2626, #f97316); padding: 36px 32px; text-align: center;">
      <h1 style="color: #fff; margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">Order Failed</h1>
      <p style="color: rgba(255,255,255,0.85); margin: 8px 0 0; font-size: 14px;">We couldn't complete this order</p>
    </div>
    <div style="padding: 40px 32px; text-align: center;">
      <p style="color: #6b7280; font-size: 15px; margin: 0 0 24px;">
        Hi <strong style="color:#111827;">{user.first_name or user.username}</strong>, unfortunately your order could not be processed.
      </p>
      <div style="background: #fef2f2; border: 2px dashed #fca5a5; border-radius: 12px; padding: 20px; display: inline-block; margin-bottom: 24px;">
        <p style="margin:0; color:#b91c1c; font-size:13px; letter-spacing: 0.5px; text-transform: uppercase;">Order ID</p>
        <p style="margin:4px 0 0; color:#dc2626; font-size:20px; font-weight:800; letter-spacing:1px; font-family:'Courier New', monospace;">{order.order_id}</p>
      </div>

      <p style="color: #4b5563; font-size: 14px; margin: 0 0 8px; text-align: left;">
        This can happen due to a payment issue, an out-of-stock item, or a temporary system error. No charge should have been made, but please double check your payment method.
      </p>
      <p style="color: #4b5563; font-size: 14px; margin: 16px 0 0; text-align: left;">
        Feel free to try placing the order again. If it keeps failing, our support team is happy to help.
      </p>
    </div>
    <div style="background: #f9fafb; padding: 20px 32px; text-align: center; border-top: 1px solid #e5e7eb;">
      <p style="color: #d1d5db; font-size: 12px; margin: 0;">This is an automated message, please do not reply.</p>
    </div>
  </div>
</body>
</html>
"""
    return _send_email_safely(subject, text_message, html_message, user.email)