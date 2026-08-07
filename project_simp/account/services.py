import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(user, otp_code):
    subject = "Verify Your Email Address – OTP Code"

    message = f"""
Hi {user.first_name or user.email},

Your email verification OTP is:

    {otp_code}

This code is valid for 10 minutes. Do not share it with anyone.

If you did not request this, please ignore this email.

— The Team
"""

    html_message = f"""
<!DOCTYPE html>
<html>
<body style="font-family: 'Segoe UI', Arial, sans-serif; background: #f4f4f8; margin: 0; padding: 40px 0;">
  <div style="max-width: 480px; margin: 0 auto; background: #fff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.08);">
    <div style="background: linear-gradient(135deg, #4f46e5, #7c3aed); padding: 36px 32px; text-align: center;">
      <h1 style="color: #fff; margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">Verify Your Email</h1>
      <p style="color: rgba(255,255,255,0.8); margin: 8px 0 0; font-size: 14px;">Use the code below to confirm your address</p>
    </div>
    <div style="padding: 40px 32px; text-align: center;">
      <p style="color: #6b7280; font-size: 15px; margin: 0 0 28px;">Hi <strong style="color: #111827;">{user.first_name or user.email}</strong>, here is your one-time password:</p>
      <div style="background: #f5f3ff; border: 2px dashed #a78bfa; border-radius: 12px; padding: 24px; display: inline-block; margin-bottom: 28px;">
        <span style="font-size: 42px; font-weight: 800; letter-spacing: 10px; color: #4f46e5; font-family: 'Courier New', monospace;">{otp_code}</span>
      </div>
      <p style="color: #9ca3af; font-size: 13px; margin: 0;">⏱ This code expires in <strong>10 minutes</strong>.</p>
      <p style="color: #9ca3af; font-size: 13px; margin: 8px 0 0;">Never share this with anyone.</p>
    </div>
    <div style="background: #f9fafb; padding: 20px 32px; text-align: center; border-top: 1px solid #e5e7eb;">
      <p style="color: #d1d5db; font-size: 12px; margin: 0;">If you didn't request this email, you can safely ignore it.</p>
    </div>
  </div>
</body>
</html>
"""

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"[OTP Email Error] Failed to send OTP to {user.email}: {e}")
        return False


def create_and_send_otp(user):
    from .models import EmailOTP

    otp_code = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=10)

    EmailOTP.objects.filter(user=user).delete()

    otp_instance = EmailOTP.objects.create(
        user=user,
        otp=otp_code,
        expires_at=expires_at,
    )

    email_sent = send_otp_email(user, otp_code)
    return otp_instance, email_sent


def verify_otp(user, submitted_otp):
    from .models import EmailOTP

    try:
        otp_record = EmailOTP.objects.get(user=user, otp=submitted_otp)
    except EmailOTP.DoesNotExist:
        return 'invalid'

    if timezone.now() > otp_record.expires_at:
        otp_record.delete()
        return 'expired'

    user.is_email_verified = True
    user.save(update_fields=['is_email_verified'])

    otp_record.delete()

    return 'valid'


def is_email_verified(user):
    return getattr(user, 'is_email_verified', False)