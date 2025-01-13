from pathlib import Path
import environ
import os

# Set the base directory for the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
env = environ.Env()

# Retrieve the secret key for the application
SECRET_KEY = env("ED_SECRET_KEY")

# Raise an error if the secret key is not set
if not SECRET_KEY:
    raise ValueError("No ED_SECRET_KEY set for production")

# Enable debug mode based on environment variable. if it does not response in production please write hardcode True/False here
# DEBUG = env("DEBUG")
DEBUG = env.bool("DEBUG", default=False)

if DEBUG:
    # Configure allowed hosts for the application
    ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(",")
else:
    # Configure allowed hosts for the application
    ALLOWED_HOSTS = env("ALLOWED_HOSTS_PRO").split(",")
    

# Set the default site ID for the Django sites framework
SITE_ID = 1


# Define the installed apps, including Django default apps and custom apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    'django.contrib.humanize',
    "django.contrib.sitemaps",
    'django_celery_results',
    'django_celery_beat',
    
    # Custom apps
    "account",
    "common",
    "rma",
    
    "django_recaptcha",# Third-party app for Google reCAPTCHA integration
]

# Use a custom user model (currently inherits the built-in Django User model)
AUTH_USER_MODEL = "account.User" 

# Configure authentication backends
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]


# Define middleware components for request processing
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Configure the root URL for the project. Do not change it
ROOT_URLCONF = "ed.urls"

# Template settings
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                
                # Custom context processor for site information from cache.
                "common.context_processor.sd_context", 
            ],
        },
    },
]

# WSGI application path
WSGI_APPLICATION = "ed.wsgi.application"

if DEBUG:

    # MySQL database dev
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env("ED_DB_NAME"),
            "USER": env("ED_DB_USER"),
            "PASSWORD": env("ED_DB_PASSWORD"),
            "HOST": env("ED_DB_HOST"),
            "PORT": env("ED_DB_PORT"),
            "OPTIONS": {
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env("ED_DB_NAME_PRO"),
            "USER": env("ED_DB_USER_PRO"),
            "PASSWORD": env("ED_DB_PASSWORD_PRO"),
            "HOST": env("ED_DB_HOST_PRO"),
            "PORT": env("ED_DB_PORT_PRO"),
            "OPTIONS": {
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
    


# Password validation settings
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


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("CACHES_LOCATION"),   
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'
CELERY_RESULT_EXTENDED = True

CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'



# Localization settings
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static and media files configuration
STATIC_URL = "/static/"
if DEBUG:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, "static"),
    ]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Set the default auto field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Google reCAPTCHA settings
RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY")
if DEBUG:
    RECAPTCHA_DOMAIN = "www.recaptcha.net"
    
    # Configure proxy settings for reCAPTCHA during development
    RECAPTCHA_PROXY = {
        "http": "http://127.0.0.1:8000",
        "https": "https://127.0.0.1:8000",
    }
SILENCED_SYSTEM_CHECKS = ["django_recaptcha.recaptcha_test_key_error"]

# Email configuration
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# Admin email addresses from .env
ADMIN = env("ADMIN").split(",")

# Security settings
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30
X_FRAME_OPTIONS = "SAMEORIGIN"
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "lax"
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o777
FILE_UPLOAD_PERMISSIONS = 0o644
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_HOST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_NAME = "ed_system"

# RMA status options
RMA_STATUS = [
    # Controls mail sending from the admin interface based on RMA status
    ("rma_sent", "RMA Sent"), 
    
    # Default status when an RMA is created from the client side
    ("pending", "Pending"), 
    
    # Status without special functionality
    ("product_received", "Product Received"), 
]


# Logging configuration
FORMATTERS = (
    {
        "verbose": {
            "format": "{levelname} {asctime} {name} {threadName} {thread} {pathname} {lineno} {funcName} {process} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {pathname} {lineno} {message}",
            "style": "{",
        },
    },
)

HANDLERS = {
    "console_handler": {
        "class": "logging.StreamHandler",
        "formatter": "simple",
        "level": "DEBUG",
    },
    "info_handler": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": os.path.join(BASE_DIR, "logs/info.log"),
        "mode": "a",
        "encoding": "utf-8",
        "formatter": "verbose",
        "level": "INFO",
        "backupCount": 5,
        "maxBytes": 1024 * 1024 * 5,  # 5 MB
    },
    "error_handler": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": os.path.join(BASE_DIR, "logs/error.log"),
        "mode": "a",
        "formatter": "verbose",
        "level": "WARNING",
        "backupCount": 5,
        "maxBytes": 1024 * 1024 * 5,  # 5 MB
    },
    "ed_handler": {
        "filename": os.path.join(BASE_DIR, "logs/debug.log"),
        "mode": "a",
        "maxBytes": 1024 * 1024 * 5,  # 5 MB
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "simple",
        "encoding": "utf-8",
        "level": "DEBUG",
        "backupCount": 5,
    },
}

# Logger configurations
LOGGERS = (
    {
        "django": {
            "handlers": ["console_handler", "info_handler"],
            "level": "INFO",
        },
        "django.request": {
            "handlers": ["error_handler"],
            "level": "INFO",
            "propagate": True,
        },
        "django.template": {
            "handlers": ["error_handler"],
            "level": "INFO",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["error_handler"],
            "level": "INFO",
            "propagate": True,
        },
        "log": {
            "handlers": ["console_handler", "ed_handler"],
            "level": "INFO",
            "level": "DEBUG",
            "propagate": True,
        },
    },
)

# Main logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": FORMATTERS[0],
    "handlers": HANDLERS,
    "loggers": LOGGERS[0],
}


