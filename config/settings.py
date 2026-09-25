"""
Django settings for config project.
"""

import os
import sys
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def env_int(name, default):
    return int(os.environ.get(name, default))


# Railway / Render / Heroku set these — used so that forgetting CAKEBAR_DEBUG
# on the server can never leave the live site in debug mode.
IS_HOSTED = any(os.environ.get(v) for v in ("RAILWAY_ENVIRONMENT", "RENDER", "DYNO"))
TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_bool("CAKEBAR_DEBUG", default=not IS_HOSTED)

# SECURITY WARNING: keep the secret key used in production secret!
# In production, set the CAKEBAR_SECRET_KEY environment variable.
_DEV_SECRET_KEY = "django-insecure-$b(16f802duktr67ia!1zg!bil!bpmwi+yr@=+s3)f(03(06em"
SECRET_KEY = os.environ.get("CAKEBAR_SECRET_KEY", _DEV_SECRET_KEY)
if not DEBUG and SECRET_KEY == _DEV_SECRET_KEY:
    raise ImproperlyConfigured("CAKEBAR_SECRET_KEY must be set when DEBUG is off.")

ALLOWED_HOSTS = [h.strip() for h in os.environ.get("CAKEBAR_ALLOWED_HOSTS", "").split(",") if h.strip()]
if DEBUG:
    ALLOWED_HOSTS += ["127.0.0.1", "localhost"]

CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get("CAKEBAR_CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]

if IS_HOSTED:
    # Railway/Render/Heroku terminate TLS at their edge and forward plain
    # HTTP with this header. Without it, request.is_secure() is always
    # False behind the proxy, and SECURE_SSL_REDIRECT below causes an
    # infinite redirect loop (every request looks insecure, so Django keeps
    # redirecting to the https:// URL it's already on).
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool("CAKEBAR_SECURE_SSL_REDIRECT", default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'rest_framework',
    'rest_framework.authtoken',
    'accounts',
    'catalog',
    'orders',
    'refunds',
    'dashboard',
    'pages',
    'promotions',
    'reviews',
    'notifications',
    'payments',
    'support',
    'api',
]

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'orders.context_processors.cart',
                'pages.context_processors.language',
                'notifications.context_processors.notifications',
                'support.context_processors.unread_chat',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASE_URL = os.environ.get("CAKEBAR_DATABASE_URL") or os.environ.get("DATABASE_URL")
if IS_HOSTED and not DATABASE_URL and not env_bool("CAKEBAR_ALLOW_SQLITE"):
    # Hosting disks are wiped on every deploy — SQLite there silently loses
    # every order and account. Attach PostgreSQL (or set CAKEBAR_ALLOW_SQLITE
    # if the SQLite file lives on a persistent volume).
    raise ImproperlyConfigured("Set CAKEBAR_DATABASE_URL (PostgreSQL) for the hosted site.")
if DATABASE_URL:
    import dj_database_url
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        # Tests run without collectstatic, so there is no manifest to read.
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage" if TESTING
        else "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
# On Railway/Render point this at a mounted persistent volume (e.g. /data/media),
# otherwise uploaded product and refund photos disappear on redeploy.
MEDIA_ROOT = Path(os.environ.get("CAKEBAR_MEDIA_ROOT", BASE_DIR / 'media'))
# Let Django serve MEDIA_ROOT itself when DEBUG is off (fine for a small shop
# on a volume; put a CDN/S3 in front once traffic grows).
SERVE_MEDIA = env_bool("CAKEBAR_SERVE_MEDIA", default=DEBUG or IS_HOSTED)

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

REFUND_WINDOW_HOURS = 72


# Email — set CAKEBAR_EMAIL_HOST etc. to send real emails. Defaults to printing
# to the console/log, which is what powers the in-app notification fallback.
EMAIL_BACKEND = os.environ.get(
    "CAKEBAR_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("CAKEBAR_EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("CAKEBAR_EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("CAKEBAR_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("CAKEBAR_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("CAKEBAR_EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = os.environ.get("CAKEBAR_DEFAULT_FROM_EMAIL", "CakeBar <no-reply@cakebar.uz>")

# Ops-only: see accounts.management.commands.bootstrap_admin. Never set these
# permanently — add them on the host to create/reset one superadmin, run the
# command once, then remove them again.
BOOTSTRAP_ADMIN_PHONE = os.environ.get("CAKEBAR_BOOTSTRAP_PHONE", "")
BOOTSTRAP_ADMIN_PASSWORD = os.environ.get("CAKEBAR_BOOTSTRAP_PASSWORD", "")

# SMS — Eskiz.uz style provider. Leave empty to skip real sending (in-app
# notifications still work without this).
ESKIZ_EMAIL = os.environ.get("ESKIZ_EMAIL", "")
ESKIZ_PASSWORD = os.environ.get("ESKIZ_PASSWORD", "")

# Telegram bot — set CAKEBAR_TELEGRAM_BOT_TOKEN to enable notifications via
# Telegram (in addition to email/in-app). Users link their account by
# messaging the bot /start with the code shown on their profile page.
TELEGRAM_BOT_TOKEN = os.environ.get("CAKEBAR_TELEGRAM_BOT_TOKEN", "")
# Empty = derived from the bot token (see notifications.telegram.webhook_secret).
TELEGRAM_WEBHOOK_SECRET = os.environ.get("CAKEBAR_TELEGRAM_WEBHOOK_SECRET", "")
# Staff group/chat that gets a message for every new order and refund request.
TELEGRAM_ADMIN_CHAT_ID = os.environ.get("CAKEBAR_TELEGRAM_ADMIN_CHAT_ID", "")
# Public https:// address of the site — needed for the Telegram Mini App.
SITE_URL = os.environ.get("CAKEBAR_SITE_URL", "")

# Send email/SMS/Telegram from a background thread instead of inside the request.
NOTIFY_ASYNC = env_bool("CAKEBAR_NOTIFY_ASYNC", default=not TESTING)

# SMS code on sign-up. Only enforced when Eskiz is configured — without an
# SMS provider there is no way to deliver the code.
PHONE_VERIFICATION = env_bool("CAKEBAR_PHONE_VERIFICATION", default=True)

# Brute-force protection: max attempts per window (per IP and per phone).
LOGIN_RATE_LIMIT = env_int("CAKEBAR_LOGIN_RATE_LIMIT", 5)
LOGIN_RATE_WINDOW_SECONDS = env_int("CAKEBAR_LOGIN_RATE_WINDOW", 15 * 60)

# --- Delivery & pricing (all amounts in so'm) ---
DELIVERY_FEE = env_int("CAKEBAR_DELIVERY_FEE", 15000)
FREE_DELIVERY_FROM = env_int("CAKEBAR_FREE_DELIVERY_FROM", 200000)  # 0 = never free
MIN_ORDER_AMOUNT = env_int("CAKEBAR_MIN_ORDER_AMOUNT", 30000)
INSCRIPTION_FEE = env_int("CAKEBAR_INSCRIPTION_FEE", 0)
DELIVERY_DAYS_AHEAD = env_int("CAKEBAR_DELIVERY_DAYS_AHEAD", 7)
DELIVERY_LEAD_HOURS = env_int("CAKEBAR_DELIVERY_LEAD_HOURS", 2)
# Card orders not paid within this many minutes are cancelled and their stock released.
UNPAID_ORDER_TTL_MINUTES = env_int("CAKEBAR_UNPAID_ORDER_TTL_MINUTES", 30)

# Payme — set both to enable real card checkout via Payme. Leave empty and
# "karta" orders are accepted the same way "naqd" ones are (demo mode).
PAYME_MERCHANT_ID = os.environ.get("CAKEBAR_PAYME_MERCHANT_ID", "")
PAYME_KEY = os.environ.get("CAKEBAR_PAYME_KEY", "")
PAYME_TEST = env_bool("CAKEBAR_PAYME_TEST", default=True)

# Click — set all three to enable real card checkout via Click.
CLICK_MERCHANT_ID = os.environ.get("CAKEBAR_CLICK_MERCHANT_ID", "")
CLICK_SERVICE_ID = os.environ.get("CAKEBAR_CLICK_SERVICE_ID", "")
CLICK_SECRET_KEY = os.environ.get("CAKEBAR_CLICK_SECRET_KEY", "")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": os.environ.get("CAKEBAR_LOG_LEVEL", "INFO")},
}
