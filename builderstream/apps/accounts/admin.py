"""Account admin configuration for custom User model."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = [
        "email", "first_name", "last_name", "is_staff",
        "email_verified", "date_joined",
    ]
    list_filter = ["is_staff", "is_superuser", "is_active", "email_verified"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-date_joined"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {
            "fields": ("first_name", "last_name", "phone", "avatar", "job_title"),
        }),
        ("Organization", {
            "fields": ("last_active_organization", "timezone", "notification_preferences"),
        }),
        ("Verification", {
            "fields": ("email_verified", "email_verification_token"),
        }),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2"),
        }),
    )
