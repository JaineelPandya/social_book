from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.views.decorators.http import require_http_methods
import os
from django.conf import settings
from django.core.mail import send_mail

from .forms import CustomUserCreationForm, UploadFileForm
from .models import UploadedFile


def home(request):
    return HttpResponse("Welcome to Social Book Home Page")


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'


@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


@login_required
def upload_books(request):
    """View for uploading books/files."""
    uploaded_files = request.user.uploaded_files.filter(is_active=True)
    
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
    
    context = {
        'form': form,
        'uploaded_files': uploaded_files,
    }
    return render(request, 'accounts/upload_books.html', context)


@login_required
@require_http_methods(["POST"])
def delete_file(request, file_id):
    """Delete an uploaded file."""
    file_obj = get_object_or_404(UploadedFile, id=file_id, user=request.user)
    
    # Delete actual file from storage
    if file_obj.file:
        file_path = file_obj.file.path
        if os.path.exists(file_path):
            os.remove(file_path)
    
    file_title = file_obj.title
    file_obj.delete()
    messages.success(request, f"File '{file_title}' deleted successfully!")
    return redirect('upload_books')


@login_required
def file_detail(request, file_id):
    """View file details."""
    file_obj = get_object_or_404(UploadedFile, id=file_id)
    
    # Check visibility
    if file_obj.user != request.user:
        if file_obj.visibility == 'private':
            return render(request, 'accounts/403.html', status=403)
        elif file_obj.visibility == 'followers':
            # Check if user follows the file owner
            pass  # Implement follower check if needed
    
    context = {'file_obj': file_obj}
    return render(request, 'accounts/file_detail.html', context)


@login_required
def postgres_dashboard(request):
    """View to display data from PostgreSQL using SQLAlchemy.
    
    This demonstrates direct SQL queries to PostgreSQL.
    Note: This view works with SQLite by default. To use PostgreSQL:
    1. Install PostgreSQL server
    2. Create a database
    3. Update the DB_URL variable below
    """
    from .postgres_utils import PostgreSQLConnection, get_users_summary, get_files_stats, get_recent_uploads
    
    # Example PostgreSQL connection URL (replace with your actual PostgreSQL database)
    # DB_URL = "postgresql://username:password@localhost:5432/database_name"
    # For now, we'll show it as a placeholder or return sample data
    
    context = {
        'page_title': 'PostgreSQL Dashboard',
        'db_connected': False,  # Set to True when PostgreSQL is configured
        'users_summary': None,
        'files_stats': None,
        'recent_uploads': [],
        'error_message': 'PostgreSQL not configured. To use PostgreSQL:'
    }
    
    # Uncomment and configure this section when you have PostgreSQL setup
    # try:
    #     db_url = "postgresql://username:password@localhost:5432/database_name"
    #     context['users_summary'] = get_users_summary(db_url)
    #     context['files_stats'] = get_files_stats(db_url)
    #     context['recent_uploads'] = get_recent_uploads(db_url)
    #     context['db_connected'] = True
    # except Exception as e:
    #     context['error_message'] = f"Database error: {str(e)}"
    
    return render(request, 'accounts/postgres_dashboard.html', context)


@login_required
def send_test_email(request):
    """Send a simple test email to the logged-in user using EMAIL settings."""
    subject = 'Social Book - Test Email'
    message = 'This is a test email sent from the Social Book application.'
    from_email = settings.EMAIL_HOST_USER or 'webmaster@localhost'
    recipient_list = [request.user.email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        messages.success(request, 'Test email sent to %s' % request.user.email)
    except Exception as e:
        messages.error(request, f'Failed to send test email: {e}')

    return redirect('dashboard')


@login_required
def my_books(request):
    """Wrapper view for 'My Books' dashboard.

    - If user has uploaded files (active), render the list view.
    - If user has no uploads, redirect to `upload_books` to prompt upload.
    """
    user_files = request.user.uploaded_files.filter(is_active=True)
    if user_files.exists():
        context = {'uploaded_files': user_files}
        return render(request, 'accounts/my_books.html', context)
    # No files uploaded yet - redirect to upload page
    return redirect('upload_books')