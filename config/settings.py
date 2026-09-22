"""
Django settings for config project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


# SECURITY WARNING: keep the secret key used in production secret!
# In production, set the CAKEBAR_SECRET_KEY environment variable.
SECRET_KEY = os.environ.get(
    "CAKEBAR_SECRET_KEY",
    "django-insecure-$b(16f802duktr67ia!1zg!bil!bpmwi+yr@=+s3)f(03(06em",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_bool("CAKEBAR_DEBUG", default=True)

ALLOWED_HOSTS = [h.strip() for h in os.environ.get("CAKEBAR_ALLOWED_HOSTS", "").split(",") if h.strip()]
if DEBUG:
    ALLOWED_HOSTS += ["127.0.0.1", "localhost"]

CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get("CAKEBAR_CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]

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
    'accounts',
    'catalog',
    'orders',
    'refunds',
    'dashboard',
    'pages',
    'promotions',
    'reviews',
    'notifications',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASE_URL = os.environ.get("CAKEBAR_DATABASE_URL")
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
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
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
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

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

# SMS — Eskiz.uz style provider. Leave empty to skip real sending (in-app
# notifications still work without this).
ESKIZ_EMAIL = os.environ.get("ESKIZ_EMAIL", "")
ESKIZ_PASSWORD = os.environ.get("ESKIZ_PASSWORD", "")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
