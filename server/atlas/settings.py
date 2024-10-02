from os import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-ggfl+qe&y3%8&=2^4pkler9o#)bo2&w^no8#vj@dy!17if9&1t"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

APP_NAME = environ.get("FLY_APP_NAME", "")
HOST_NAME = environ.get("SCAIFE_HOST")

ALLOWED_HOSTS = [
    "localhost",
    f"{APP_NAME}.fly.dev",
    f"{HOST_NAME}"
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    "atlas",

    "atlas.dictionaries",
    "atlas.morphology",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "atlas.urls"

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
    },
]

WSGI_APPLICATION = "atlas.wsgi.application"


# Database

DB_DIR = Path("/server/db")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DB_DIR / "default.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


## ATLAS SPECIFIC

ATLAS_DATA_DIR = BASE_DIR.parent / "test-data"


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "sv-cache",
    },
}

XSL_STYLESHEET_PATH = environ.get("XSL_STYLESHEET_PATH", BASE_DIR / "atlas/tei.xsl")

CTS_RESOLVER_CACHE_LOCATION = environ.get("CTS_RESOLVER_CACHE_LOCATION", "cts_resolver_cache")
SCAIFE_VIEWER_CORE_RESOLVER_CACHE_LABEL = "cts-resolver"
CTS_RESOLVER_CACHE_KWARGS = {
    "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
    "LOCATION": CTS_RESOLVER_CACHE_LOCATION,
}
CACHES.update({
    SCAIFE_VIEWER_CORE_RESOLVER_CACHE_LABEL: CTS_RESOLVER_CACHE_KWARGS,
})

resolver = environ.get("CTS_RESOLVER", "local")
if resolver == "api":
    CTS_API_ENDPOINT = environ.get("CTS_API_ENDPOINT", "https://scaife-cts-dev.perseus.org/api/cts")
    CTS_RESOLVER = {
        "type": "api",
        "kwargs": {
            "endpoint": CTS_API_ENDPOINT,
        },
    }
    CTS_LOCAL_TEXT_INVENTORY = "ti.xml" if DEBUG else None
elif resolver == "local":
    CTS_LOCAL_DATA_PATH = environ.get("CTS_LOCAL_DATA_PATH", "data/cts")
    CTS_RESOLVER = {
        "type": "local",
        "kwargs": {
            "data_path": CTS_LOCAL_DATA_PATH,
        },
    }

