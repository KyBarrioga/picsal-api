"""Django settings for the Picsal API project."""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


BASE_DIR = Path(__file__).resolve().parent.parent


def get_env(name: str, default: str | None = None) -> str | None:
    """Read an environment variable with whitespace trimmed."""
    value = os.environ.get(name, default)
    return value.strip() if isinstance(value, str) else value


def get_bool(name: str, default: bool = False) -> bool:
    """Read a boolean environment variable."""
    value = get_env(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def get_list(name: str, default: list[str] | None = None) -> list[str]:
    """Read a comma-separated environment variable into a list."""
    value = get_env(name)
    if not value:
        return default or []
    return [item.strip() for item in value.split(",") if item.strip()]


def build_database_config() -> dict[str, object]:
    """Build database settings from DATABASE_URL or individual env vars."""
    database_url = get_env("DATABASE_URL")
    if database_url:
        parsed = urlparse(database_url)
        config = {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": parsed.path.lstrip("/"),
            "USER": unquote(parsed.username) if parsed.username else None,
            "PASSWORD": unquote(parsed.password) if parsed.password else None,
            "HOST": parsed.hostname,
            "PORT": parsed.port or 5432,
        }
        query = parse_qs(parsed.query)
        options = {}
        if "sslmode" in query and query["sslmode"]:
            options["sslmode"] = query["sslmode"][-1]
        if "connect_timeout" in query and query["connect_timeout"]:
            options["connect_timeout"] = query["connect_timeout"][-1]
        if options:
            config["OPTIONS"] = options
        return config

    db_name = get_env("DB_NAME")
    if db_name:
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": db_name,
            "USER": get_env("DB_USER"),
            "PASSWORD": get_env("DB_PASSWORD"),
            "HOST": get_env("DB_HOST", "localhost"),
            "PORT": get_env("DB_PORT", "5432"),
        }

    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }


SECRET_KEY = get_env("DJANGO_SECRET_KEY", "unsafe-dev-secret-key")
DEBUG = get_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = get_list("DJANGO_ALLOWED_HOSTS", ["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "authn",
    "core",
    "user",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "app.wsgi.application"
ASGI_APPLICATION = "app.asgi.application"

DATABASES = {"default": build_database_config()}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = get_list("DJANGO_CORS_ALLOWED_ORIGINS", [])

SUPABASE_URL = get_env("SUPABASE_URL", "")
SUPABASE_ANON_KEY = get_env("SUPABASE_ANON_KEY", "")
SUPABASE_JWKS_URL = get_env("SUPABASE_JWKS_URL", "")
SUPABASE_JWT_ISSUER = get_env("SUPABASE_JWT_ISSUER", "")
SUPABASE_JWT_SECRET = get_env("SUPABASE_JWT_SECRET", "")
SUPABASE_JWT_AUDIENCE = get_env("SUPABASE_JWT_AUDIENCE", "")
SUPABASE_JWT_ALGORITHM = get_env("SUPABASE_JWT_ALGORITHM", "HS256")

CLOUDFLARE_R2_ACCOUNT_ID = get_env("CLOUDFLARE_R2_ACCOUNT_ID", "")
CLOUDFLARE_R2_ACCESS_KEY_ID = get_env("CLOUDFLARE_R2_ACCESS_KEY_ID", "")
CLOUDFLARE_R2_SECRET_ACCESS_KEY = get_env("CLOUDFLARE_R2_SECRET_ACCESS_KEY", "")
CLOUDFLARE_R2_BUCKET = get_env("CLOUDFLARE_R2_BUCKET", "")
CLOUDFLARE_R2_PUBLIC_BASE_URL = get_env("CLOUDFLARE_R2_PUBLIC_BASE_URL", "")

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "core.authentication.SupabaseJWTAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
}

PROFILE_TABLE_NAME = get_env("SUPABASE_PROFILE_TABLE", "profiles")
PROFILE_SCHEMA_NAME = get_env("SUPABASE_PROFILE_SCHEMA", "public")
PROFILE_PROTECTED_COLUMNS = {
    "id",
    "email",
    "role",
    "created_at",
    "updated_at",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Picsal API",
    "DESCRIPTION": "Core and user API for Picsal using Supabase and Cloudflare R2.",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "COMPONENT_SPLIT_REQUEST": True,
    "SECURITY": [{"BearerAuth": []}],
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Paste a Supabase access token as: Bearer <token>",
            }
        }
    },
}
