"""
Base settings for BuilderStream project.
Shared across all environments.
"""
import os
from datetime import timedelta
from pathlib import Path

import environ
from celery.schedules import crontab

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Security
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "corsheaders",
    "storages",
    "django_celery_beat",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
    "drf_spectacular",
    "imagekit",
]

LOCAL_APPS = [
    "apps.core",
    "apps.tenants",
    "apps.accounts",
    "apps.billing",
    "apps.projects",
    "apps.crm",
    "apps.estimating",
    "apps.scheduling",
    "apps.financials",
    "apps.clients",
    "apps.documents",
    "apps.field_ops",
    "apps.quality_safety",
    "apps.payroll",
    "apps.service",
    "apps.analytics",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.tenants.middleware.TenantMiddleware",
    "apps.billing.middleware.SubscriptionRequiredMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database - PostgreSQL with connection pooling
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", default="builderstream"),
        "USER": env("DB_USER", default="postgres"),
        "PASSWORD": env("DB_PASSWORD", default="postgres"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
        "CONN_MAX_AGE": 600,
        "CONN_HEALTH_CHECKS": True,
    }
}

# Custom User Model
AUTH_USER_MODEL = "accounts.User"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media files
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Sites framework
SITE_ID = 1

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
}

# Simple JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "TOKEN_OBTAIN_SERIALIZER": "apps.accounts.serializers.CustomTokenObtainPairSerializer",
}

# DRF Spectacular (OpenAPI)
SPECTACULAR_SETTINGS = {
    "TITLE": "BuilderStream API",
    "DESCRIPTION": "Construction Management Platform API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/v1/",
    "COMPONENT_SPLIT_REQUEST": True,
}

# CORS
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:5173"],
)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-organization-id",
]

# Cache (Redis db 1, separate from Celery on db 0)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_CACHE_URL", default="redis://localhost:6379/1"),
    }
}

# Celery
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BEAT_SCHEDULE = {
    "calculate-health-scores": {
        "task": "projects.calculate_all_health_scores",
        "schedule": 3600,  # every hour
    },
    "generate-action-items": {
        "task": "projects.generate_action_items",
        "schedule": 1800,  # every 30 minutes
    },
    # CRM tasks
    "process-time-based-automations": {
        "task": "crm.process_time_based_automations",
        "schedule": 900,  # every 15 minutes
    },
    "calculate-lead-scores": {
        "task": "crm.calculate_lead_scores",
        "schedule": 3600,  # hourly
    },
    "send-follow-up-reminders": {
        "task": "crm.send_follow_up_reminders",
        "schedule": crontab(hour=9, minute=0),  # daily at 9am
    },
    # Client portal tasks
    "send-client-daily-digest": {
        "task": "clients.send_client_daily_digest",
        "schedule": crontab(hour=8, minute=0),  # daily at 8am
    },
    "send-approval-reminders": {
        "task": "clients.send_approval_reminders",
        "schedule": crontab(hour=9, minute=30),  # daily at 9:30am
    },
    # Document & Photo tasks
    "check-rfi-due-dates": {
        "task": "documents.check_rfi_due_dates",
        "schedule": crontab(hour=7, minute=0),  # daily at 7am
    },
    "check-document-expirations": {
        "task": "documents.check_document_expirations",
        "schedule": crontab(hour=2, minute=0, day_of_week=1),  # Monday 2am
    },
    # Scheduling tasks
    "recalculate-critical-paths": {
        "task": "scheduling.recalculate_critical_paths",
        "schedule": 3600,  # hourly
    },
    "check-schedule-conflicts": {
        "task": "scheduling.check_schedule_conflicts",
        "schedule": crontab(hour=6, minute=0),  # daily at 6am
    },
    "calculate-equipment-depreciation": {
        "task": "scheduling.calculate_equipment_depreciation",
        "schedule": crontab(hour=1, minute=0, day_of_month=1),  # monthly at 1am on 1st
    },
    # Financial tasks
    "check-overdue-invoices": {
        "task": "financials.check_overdue_invoices",
        "schedule": crontab(hour=7, minute=30),  # daily at 7:30am
    },
    "calculate-budget-variances": {
        "task": "financials.calculate_budget_variances",
        "schedule": 3600,  # hourly
    },
    "generate-aging-report": {
        "task": "financials.generate_aging_report",
        "schedule": crontab(hour=3, minute=0, day_of_week=1),  # Monday 3am
    },
    # Field Operations tasks
    "auto-clock-out": {
        "task": "field_ops.auto_clock_out",
        "schedule": crontab(hour=23, minute=59),  # nightly at 11:59pm
    },
    "reminder-daily-log": {
        "task": "field_ops.reminder_daily_log",
        "schedule": crontab(hour=16, minute=0),  # daily at 4pm
    },
    "calculate-overtime": {
        "task": "field_ops.calculate_overtime",
        "schedule": crontab(hour=0, minute=30),  # nightly at 12:30am
    },
    # Quality & Safety tasks
    "check-overdue-inspections": {
        "task": "quality_safety.check_overdue_inspections",
        "schedule": crontab(hour=7, minute=0),  # daily at 7am
    },
    "check-overdue-deficiencies": {
        "task": "quality_safety.check_overdue_deficiencies",
        "schedule": crontab(hour=8, minute=0),  # daily at 8am
    },
    "generate-weekly-safety-report": {
        "task": "quality_safety.generate_weekly_safety_report",
        "schedule": crontab(hour=6, minute=0, day_of_week=1),  # Monday 6am
    },
    # Payroll & Workforce tasks
    "check-certification-expirations": {
        "task": "payroll.check_certification_expirations",
        "schedule": crontab(hour=6, minute=30),  # daily at 6:30am
    },
    "prevailing-wage-compliance-check": {
        "task": "payroll.prevailing_wage_compliance_check",
        "schedule": crontab(hour=5, minute=0, day_of_week=1),  # Monday 5am
    },
    # Service & Warranty tasks
    "check-expiring-warranties": {
        "task": "service.check_expiring_warranties",
        "schedule": crontab(hour=7, minute=0),  # daily 7am
    },
    "expire-old-agreements": {
        "task": "service.expire_old_agreements",
        "schedule": crontab(hour=7, minute=15),  # daily 7:15am
    },
    "generate-recurring-invoices": {
        "task": "service.generate_recurring_invoices",
        "schedule": crontab(hour=8, minute=0, day_of_month=1),  # 1st of month 8am
    },
    # Analytics & Reporting tasks
    "calculate-kpis": {
        "task": "analytics.calculate_kpis",
        "schedule": crontab(hour=2, minute=0),  # daily 2am
    },
    "run-scheduled-reports": {
        "task": "analytics.run_scheduled_reports",
        "schedule": crontab(hour=6, minute=0),  # daily 6am
    },
    "generate-weekly-summary": {
        "task": "analytics.generate_weekly_summary",
        "schedule": crontab(hour=5, minute=0, day_of_week=1),  # Monday 5am
    },
}

# AWS S3 / django-storages
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="builderstream-media")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="us-east-1")
AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN", default="")
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
AWS_QUERYSTRING_AUTH = True  # Presigned URL support
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None

# django-allauth
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Social Auth Providers
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "APP": {
            "client_id": env("GOOGLE_CLIENT_ID", default=""),
            "secret": env("GOOGLE_CLIENT_SECRET", default=""),
        },
    },
    "github": {
        "SCOPE": ["user:email"],
        "APP": {
            "client_id": env("GITHUB_CLIENT_ID", default=""),
            "secret": env("GITHUB_CLIENT_SECRET", default=""),
        },
    },
}

# Frontend URL (for email verification links, password reset links)
FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:5173")

# Stripe
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY", default="")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="")

# Email
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@builderstream.com")

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": env("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
