"""Custom user model with email-based authentication."""
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone as django_tz


class CustomUserManager(BaseUserManager):
    """Manager for email-based user authentication."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required")
        email = self.normalize_email(email).lower()
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


US_TIMEZONES = [
    ("America/New_York", "Eastern"),
    ("America/Chicago", "Central"),
    ("America/Denver", "Mountain"),
    ("America/Los_Angeles", "Pacific"),
    ("America/Anchorage", "Alaska"),
    ("Pacific/Honolulu", "Hawaii"),
    ("America/Phoenix", "Arizona"),
    ("UTC", "UTC"),
]


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with email as the primary identifier.

    Uses AbstractBaseUser + PermissionsMixin for full control over fields.
    No username field -- email is the sole login identifier.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True)

    # Status flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Email verification
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(null=True, blank=True)

    # Organization context
    last_active_organization = models.ForeignKey(
        "tenants.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="active_users",
    )

    # Preferences
    timezone = models.CharField(
        max_length=50, default="America/Chicago", choices=US_TIMEZONES
    )
    notification_preferences = models.JSONField(default=dict, blank=True)

    # Timestamps
    date_joined = models.DateTimeField(default=django_tz.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name
