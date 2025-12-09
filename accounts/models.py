from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import date
from django.core.validators import FileExtensionValidator

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    # ❌ REMOVE USERNAME COMPLETELY
    username = None

    # ✅ EMAIL AS PRIMARY LOGIN FIELD
    email = models.EmailField(_("email address"), unique=True)

    # ✅ YOUR CUSTOM FIELDS
    public_visibility = models.BooleanField(default=True)
    birth_year = models.IntegerField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    followers_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    @property
    def age(self):
        if self.birth_year:
            return date.today().year - self.birth_year
        return None

    def __str__(self):
        return self.email


class UploadedFile(models.Model):
    """Model for storing uploaded books/files with metadata."""
    
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('public', 'Public'),
        ('followers', 'Followers Only'),
    ]
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='uploaded_files'
    )
    
    # File and metadata
    title = models.CharField(max_length=255, help_text="Title of the book/file")
    description = models.TextField(blank=True, null=True, help_text="Description or summary")
    file = models.FileField(
        upload_to='books/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpeg', 'jpg'])],
        help_text="Only PDF, JPEG formats allowed"
    )
    
    # Publishing details
    year_published = models.IntegerField(
        blank=True,
        null=True,
        help_text="Year the book was published"
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Cost of the book (0 = free)"
    )
    
    # Visibility and status
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='private',
        help_text="Who can view this file"
    )
    is_active = models.BooleanField(default=True, help_text="File is available for download")
    
    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # File metadata
    file_size = models.BigIntegerField(default=0, help_text="File size in bytes")
    downloads_count = models.IntegerField(default=0, help_text="Number of downloads")
    
    class Meta:
        verbose_name = "Uploaded File"
        verbose_name_plural = "Uploaded Files"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} by {self.user.email}"
    
    def get_file_size_display(self):
        """Return human-readable file size."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
