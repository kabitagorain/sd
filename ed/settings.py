from pathlib import Path
import environ
import os

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
env = environ.Env()

SECRET_KEY = env('ED_SECRET_KEY')

if not SECRET_KEY:
    raise ValueError('No ED_SECRET_KEY set for production')

DEBUG = env("DEBUG")

ALLOWED_HOSTS = env('ALLOWED_HOSTS').split(',')

SITE_ID = 1

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',  
    'account',
    'common',
    'rma',
    'django_recaptcha',
]

AUTH_USER_MODEL = 'account.User'
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ed.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'common.context_processor.sd_context'
            ],
        },
    },
]

WSGI_APPLICATION = 'ed.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',        
        'NAME': env("ED_DB_NAME"),
        'USER': env("ED_DB_USER"),
        'PASSWORD': env("ED_DB_PASSWORD"),
        'HOST': env("ED_DB_HOST"),
        'PORT': env("ED_DB_PORT"),
        'OPTIONS': {
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache'),
        'TIMEOUT': 3600,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

    


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = '/static/'

if DEBUG:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
    ]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY')
if DEBUG:
    RECAPTCHA_DOMAIN = 'www.recaptcha.net'
    RECAPTCHA_PROXY = {'http': 'http://127.0.0.1:8000', 'https': 'https://127.0.0.1:8000'}
SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'   
else:    
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'    
    
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT= env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True

ADMIN = env('ADMIN').split(',')

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30
X_FRAME_OPTIONS = 'SAMEORIGIN'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'lax'
FILE_UPLOAD_DIRECTORY_PERMISSIONS =0o777
FILE_UPLOAD_PERMISSIONS = 0o644
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_HOST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_NAME = 'ed_system'

RMA_STATUS = [    
    ("rma_sent", "RMA Sent"), 
    ("pending", "Pending"),   
    ("product_received", "Product Received")    
]




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
        "level": "DEBUG"
    },
    "info_handler": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": os.path.join(BASE_DIR, 'logs/info.log' ),
        "mode": "a",
        "encoding": "utf-8",
        "formatter": "verbose",
        "level": "INFO",
        "backupCount": 5,
        "maxBytes": 1024 * 1024 * 5,  # 5 MB
    },
    "error_handler": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": os.path.join(BASE_DIR, 'logs/error.log' ),
        "mode": "a",
        "formatter": "verbose",
        "level": "WARNING",
        "backupCount": 5,
        "maxBytes": 1024 * 1024 * 5,  # 5 MB
    },
    'ed_handler': {
        "filename": os.path.join(BASE_DIR, 'logs/debug.log' ),
        "mode": "a",
        "maxBytes": 1024 * 1024 * 5,  # 5 MB            
        'class': 'logging.handlers.RotatingFileHandler',
        "formatter": "simple",
        "encoding": "utf-8",
        "level": "DEBUG",
        "backupCount": 5,
        
    }
}

LOGGERS = (
    {
        "django": {
            "handlers": ["console_handler", "info_handler"],
            "level": "INFO",
           
        },
        "django.request": {
            "handlers": ["error_handler"],
            'level': 'INFO',             
            "propagate": True,
        },
        "django.template": {
            "handlers": ["error_handler"],
            'level': 'INFO',             
            "propagate": False,
        },
        "django.server": {
            "handlers": ["error_handler"],
            'level': 'INFO',             
            "propagate": True,
        },
        'log': {
            'handlers': ['console_handler', 'ed_handler'],
            'level': 'INFO', 
            'level': 'DEBUG',   
            "propagate": True,    
            
        },
    },
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": FORMATTERS[0],
    "handlers": HANDLERS,
    "loggers": LOGGERS[0],
}
