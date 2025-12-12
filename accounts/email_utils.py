"""Email utility functions for Social Book."""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from .tokens import account_activation_token
import logging

logger = logging.getLogger(__name__)


def send_activation_email(user, request):
    """Send account activation email to user."""
    try:
        current_site = get_current_site(request)
        subject = 'Activate Your Social Book Account'
        
        # Generate activation token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        
        # Build activation URL
        activation_url = f"http://{current_site.domain}/accounts/activate/{uid}/{token}/"
        
        # Render email template
        message = render_to_string('emails/activation_email.html', {
            'user': user,
            'activate_url': activation_url,
            'domain': current_site.domain,
        })
        
        # Send email
        send_mail(
            subject=subject,
            message='',  # Plain text fallback
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False,
        )
        
        logger.info(f"Activation email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send activation email to {user.email}: {str(e)}")
        return False


def send_login_notification(user, request=None):
    """Send login notification email to user."""
    try:
        from datetime import datetime
        
        subject = 'New Login to Your Social Book Account'
        
        # Get login details
        login_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        ip_address = get_client_ip(request) if request else "Unknown"
        
        # Render email template
        message = render_to_string('emails/login_notification.html', {
            'user': user,
            'login_time': login_time,
            'ip_address': ip_address,
        })
        
        # Send email
        send_mail(
            subject=subject,
            message='',  # Plain text fallback
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False,
        )
        
        logger.info(f"Login notification sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send login notification to {user.email}: {str(e)}")
        return False


def get_client_ip(request):
    """Get client IP address from request."""
    if not request:
        return "Unknown"
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
