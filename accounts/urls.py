from django.urls import include, path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public routes (no login required)
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('welcome/', views.welcome, name='welcome'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    
    # Token-based authentication (creates Django session)
    path('token-session-login/', views.token_session_login, name='token_session_login'),
    
    # Protected routes (require login via @login_required)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('upload-books/', views.upload_books, name='upload_books'),
    path('my-books/', views.my_books, name='my_books'),
    path('file/<int:file_id>/', views.file_detail, name='file_detail'),
    path('file/<int:file_id>/delete/', views.delete_file, name='delete_file'),
    path('enroll-data/<int:file_id>/', views.enroll_data, name='enroll_data'),
    path('send-test-email/', views.send_test_email, name='send_test_email'),
    path('postgres-dashboard/', views.postgres_dashboard, name='postgres_dashboard'),
    
    # Authors app
    path('authors/', include('authors.urls', namespace='authors')),
]