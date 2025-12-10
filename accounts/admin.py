from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UploadedFile, EnrolledData


# ✅ Custom User Admin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "is_staff", "is_active")
    list_filter = ("email", "is_staff", "is_active")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("birth_year", "address", "bio", "public_visibility")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2",
                "is_staff", "is_active"
            )
        }),
    )

    search_fields = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)


# ✅ Uploaded File Admin
@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "visibility", "is_active", "uploaded_at")
    list_filter = ("visibility", "is_active")
    search_fields = ("title", "user__email")
    readonly_fields = ("uploaded_at", "updated_at", "file_size", "downloads_count")
    ordering = ("-uploaded_at",)


# ✅ ✅ Enrolled Data Admin
@admin.register(EnrolledData)
class EnrolledDataAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "user", "created_at", "updated_at")
    search_fields = ("file__title", "user__email")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    ordering = ("-created_at",)
