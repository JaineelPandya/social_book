"""
Quick email configuration test script.
Run this to verify your SMTP settings are correct.
"""

from django.core.mail import send_mail
from django.conf import settings

def test_email():
    """Test sending an email."""
    try:
        send_mail(
            subject='Social Book - Test Email',
            message='If you receive this, your email configuration is working!',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],  # Send to yourself
            fail_silently=False,
        )
        print("✅ Test email sent successfully!")
        print(f"Check your inbox at: {settings.EMAIL_HOST_USER}")
        return True
    except Exception as e:
        print(f"❌ Failed to send test email:")
        print(f"Error: {str(e)}")
        print("\nPlease check your SMTP settings in settings.py:")
        print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        print("EMAIL_HOST_PASSWORD: [hidden]")
        return False

if __name__ == "__main__":
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_book.settings')
    django.setup()
    test_email()
