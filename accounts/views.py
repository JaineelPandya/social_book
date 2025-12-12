"""
Django views for the Social Book application.

Handles:
- User authentication (token + session)
- File uploads and management
- Enrollment data collection
- Dashboard and profile views
"""

import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import login as django_login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .forms import CustomUserCreationForm, UploadFileForm, ProfileUpdateForm
from .models import UploadedFile, EnrolledData, CustomUser


# ============================================================================
# PUBLIC VIEWS (No login required)
# ============================================================================

def home(request):
    """Landing page with Create Account and Login buttons."""
    return render(request, 'accounts/home.html')


def register(request):
    """User registration view with email verification."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Create user but don't activate yet
            user = form.save(commit=False)
            user.is_active = False  # User must verify email first
            user.email_verified = False
            user.save()
            
            # Send activation email
            from .email_utils import send_activation_email
            email_sent = send_activation_email(user, request)
            
            if email_sent:
                messages.success(
                    request,
                    'Account created! Please check your email to activate your account.'
                )
            else:
                messages.warning(
                    request,
                    'Account created but activation email failed to send. Please contact support.'
                )
            
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def welcome(request):
    """Welcome/landing page shown after successful registration."""
    return render(request, 'accounts/welcome.html')


def login_page(request):
    """Login page view."""
    return render(request, 'accounts/login.html')


def logout_view(request):
    """Logout view that clears session and redirects to home."""
    logout(request)
    return redirect('home')


def activate_account(request, uidb64, token):
    """Activate user account via email verification link."""
    from django.utils.http import urlsafe_base64_decode
    from django.utils.encoding import force_str
    from .tokens import account_activation_token
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_verified = True
        user.save()
        
        messages.success(
            request,
            '✅ Your email has been verified! You can now sign in to your account.'
        )
        return redirect('login')
    else:
        messages.error(
            request,
            '❌ Activation link is invalid or has expired. Please contact support.'
        )
        return redirect('home')


class CustomLoginView(LoginView):
    """Django's built-in login view for form-based authentication."""
    template_name = 'accounts/login.html'


# ============================================================================
# TOKEN-BASED AUTHENTICATION
# ============================================================================

@api_view(['POST'])
@permission_classes([])
def token_session_login(request):
    """
    Create a session cookie from an auth token.
    This endpoint is called client-side after obtaining a token from Djoser.
    """
    token_str = request.data.get('token')
    
    if not token_str:
        return Response(
            {'detail': 'No token provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Look up the Token object
        token_obj = Token.objects.get(key=token_str)
        user = token_obj.user
        
        # Check if email is verified
        if not user.email_verified:
            return Response(
                {'detail': 'Please verify your email before logging in. Check your inbox for the activation link.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create Django session
        django_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        # Send login notification email
        from .email_utils import send_login_notification
        send_login_notification(user, request)
        
        return Response({'detail': 'Session created successfully'}, status=status.HTTP_200_OK)
    
    except Token.DoesNotExist:
        return Response(
            {'detail': 'Invalid token'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        return Response(
            {'detail': f'Login failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



# ============================================================================
# AUTHENTICATED VIEWS (Require login via @login_required)
# ============================================================================

@login_required(login_url='login')
def dashboard(request):
    """User dashboard - shows overview and stats."""
    total_users = CustomUser.objects.filter(is_active=True).count()
    total_books = UploadedFile.objects.filter(is_active=True).count()
    
    context = {
        'user': request.user,
        'total_users': total_users,
        'total_books': total_books,
        'total_files': request.user.uploaded_files.filter(is_active=True).count(),
        'total_enrollments': EnrolledData.objects.filter(user=request.user).count(),
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
def profile(request):
    """User profile view with public/private visibility toggle."""
    from .forms import ProfileUpdateForm
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})


@login_required(login_url='login')
def upload_books(request):
    """
    Upload books/files view.
    
    GET: Display upload form and list of user's files
    POST: Handle file upload with metadata
    """
    uploaded_files = UploadedFile.objects.filter(user=request.user, is_active=True)

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = form.save(commit=False)
            file_obj.user = request.user

            # Store file size
            if request.FILES.get('file'):
                file_obj.file_size = request.FILES['file'].size

            file_obj.save()
            messages.success(request, f"File '{file_obj.title}' uploaded successfully!")
            return redirect('upload_books')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UploadFileForm()

    return render(request, 'accounts/upload_books.html', {
        'form': form,
        'uploaded_files': uploaded_files
    })


@login_required(login_url='login')
@require_http_methods(["POST"])
def delete_file(request, file_id):
    """
    Delete an uploaded file.
    
    Only the file owner can delete their own files.
    DELETE action removes file from storage and database.
    """
    file_obj = get_object_or_404(UploadedFile, id=file_id, user=request.user)

    # Delete actual file from storage
    if file_obj.file and os.path.exists(file_obj.file.path):
        os.remove(file_obj.file.path)

    file_title = file_obj.title
    file_obj.delete()
    messages.success(request, f"File '{file_title}' deleted successfully!")
    return redirect('upload_books')


@login_required(login_url='login')
def file_detail(request, file_id):
    """
    View file details and metadata.
    
    Shows file info, visibility settings, and actions.
    Only file owner can see private files.
    """
    file_obj = get_object_or_404(UploadedFile, id=file_id)

    # Check visibility
    if file_obj.user != request.user:
        if file_obj.visibility == 'private':
            return render(request, 'accounts/403.html', status=403)

    context = {'file_obj': file_obj}
    return render(request, 'accounts/file_detail.html', context)


@login_required(login_url='login')
def my_books(request):
    """
    'My Books' dashboard showing user's uploaded files.
    
    Shows all user's uploaded books with PDF download links.
    """
    user_files = UploadedFile.objects.filter(user=request.user, is_active=True).order_by('-uploaded_at')
    context = {'uploaded_files': user_files}
    return render(request, 'accounts/my_books.html', context)


@login_required(login_url='login')
def enroll_data(request, file_id):
    """
    Enrollment data collection view.
    
    Allows users to enter enrollment details (name, price) for their files.
    Data is stored in JSON payload for flexibility.
    
    GET: Display form with existing data (if any)
    POST: Save/update enrollment data
    """
    file_obj = get_object_or_404(UploadedFile, id=file_id, user=request.user)

    # Get or create enrollment record
    enrolled, created = EnrolledData.objects.get_or_create(
        file=file_obj,
        user=request.user
    )

    if request.method == 'POST':
        # Collect form fields
        name = request.POST.get('name', '').strip()
        price = request.POST.get('price', '').strip()

        # Update or create payload
        payload = enrolled.payload or {}
        if name:
            payload['name'] = name
        if price:
            payload['price'] = price

        enrolled.payload = payload
        enrolled.save()

        messages.success(request, "Enrollment data saved!")
        return redirect('enroll_data', file_id=file_id)

    context = {
        'file': file_obj,
        'enrolled': enrolled,
    }
    return render(request, 'accounts/enroll_data.html', context)


@login_required(login_url='login')
def send_test_email(request):
    """
    Send a test email to the logged-in user.
    
    Uses SMTP settings from environment or Django settings.
    """
    subject = 'Social Book - Test Email'
    message = 'This is a test email sent from the Social Book application.'
    from_email = settings.EMAIL_HOST_USER or 'webmaster@localhost'
    recipient_list = [request.user.email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        messages.success(request, f'Test email sent to {request.user.email}')
    except Exception as e:
        messages.error(request, f'Failed to send test email: {e}')

    return redirect('dashboard')


@login_required(login_url='login')
def postgres_dashboard(request):
    """
    PostgreSQL Dashboard view.
    
    Displays database statistics when PostgreSQL is configured.
    Falls back to placeholder view for SQLite.
    """
    context = {
        'page_title': 'PostgreSQL Dashboard',
        'db_connected': False,
        'users_summary': None,
        'files_stats': None,
        'recent_uploads': [],
        'error_message': 'PostgreSQL not configured. Using SQLite fallback.'
    }

    # TODO: Implement PostgreSQL stats here when needed
    # from .postgres_utils import get_users_summary, get_files_stats, get_recent_uploads
    # try:
    #     context['users_summary'] = get_users_summary()
    #     context['files_stats'] = get_files_stats()
    #     context['recent_uploads'] = get_recent_uploads()
    #     context['db_connected'] = True
    # except Exception as e:
    #     context['error_message'] = f"Database error: {str(e)}"

    return render(request, 'accounts/postgres_dashboard.html', context)
