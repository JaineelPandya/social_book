from django.urls import include, path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Upload books
    path('upload-books/', views.upload_books, name='upload_books'),
    path('file/<int:file_id>/', views.file_detail, name='file_detail'),
    path('file/<int:file_id>/delete/', views.delete_file, name='delete_file'),
    
    # PostgreSQL Dashboard (SQLAlchemy)
    path('postgres-dashboard/', views.postgres_dashboard, name='postgres_dashboard'),
    
    # Authors listing (authors app defines `app_name = "authors"`)
    path('authors/', include('authors.urls', namespace='authors')),
]