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
from django.contrib.auth import login as django_login
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token

from .forms import CustomUserCreationForm, UploadFileForm
from .models import UploadedFile, EnrolledData, CustomUser


# ============================================================================
# PUBLIC VIEWS (No login required)
# ============================================================================

def home(request):
    """Landing page with Create Account and Login buttons."""
    return render(request, 'accounts/home.html')


def register(request):
    """User registration view with auto-login."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-login the user after registration
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            django_login(request, user)
            return redirect('welcome')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def welcome(request):
    """Welcome/landing page shown after successful registration."""
    return render(request, 'accounts/welcome.html')


class CustomLoginView(LoginView):
    """Django's built-in login view for form-based authentication."""
    template_name = 'accounts/login.html'


# ============================================================================
# TOKEN-BASED AUTHENTICATION
# ============================================================================

@csrf_exempt
def token_session_login(request):
    """
    Convert DRF auth token into Django session login.
    
    POST accepts JSON: {"token": "<token_key>"}
    or Authorization header: "Token <token_key>"
    
    Returns JSON response with success status and creates Django session.
    This enables @login_required to work after token-based login.
    """
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed."}, status=405)

    try:
        # Try to get token from JSON body
        try:
            payload = json.loads(request.body.decode() or "{}")
            token_key = payload.get("token")
        except Exception:
            token_key = None

        # Fallback: Try Authorization header "Token <key>"
        if not token_key:
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "token":
                token_key = parts[1]

        if not token_key:
            return JsonResponse({"detail": "No token provided."}, status=400)

        # Validate token
        token = Token.objects.select_related("user").get(key=token_key)
        user = token.user

        # Set backend explicitly for session login
        user.backend = "django.contrib.auth.backends.ModelBackend"
        
        # Create Django session
        django_login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        return JsonResponse({
            "detail": "Session created.",
            "user_id": user.id,
            "email": user.email
        }, status=200)

    except Token.DoesNotExist:
        return JsonResponse({"detail": "Invalid token."}, status=401)
    except Exception as e:
        return JsonResponse({"detail": f"Server error: {str(e)}"}, status=500)


# ============================================================================
# AUTHENTICATED VIEWS (Require login via @login_required)
# ============================================================================

@login_required(login_url='login')
def dashboard(request):
    """User dashboard - shows overview and stats."""
    context = {
        'user': request.user,
        'total_files': request.user.uploaded_files.filter(is_active=True).count(),
        'total_enrollments': EnrolledData.objects.filter(user=request.user).count(),
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
def profile(request):
    """User profile view."""
    return render(request, 'accounts/profile.html')


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
    'My Books' dashboard wrapper.
    
    Shows user's uploaded files if they exist.
    Redirects to upload page if no files.
    """
    user_files = UploadedFile.objects.filter(user=request.user, is_active=True)
    if user_files.exists():
        context = {'uploaded_files': user_files}
        return render(request, 'accounts/my_books.html', context)
    return redirect('upload_books')


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
