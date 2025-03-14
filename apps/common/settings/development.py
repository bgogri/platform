from apps.common.settings.base import *

DEBUG = True
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
ALLOWED_HOSTS += ["127.0.0.1", "localhost"]
TEMPLATES[0]["OPTIONS"]["auto_reload"] = DEBUG

# Required for django-debug-toolbar
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

# AWS S3 Configuration
if AWS_STORAGE_BUCKET_NAME := os.getenv("AWS_STORAGE_BUCKET_NAME"):
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    AWS_STATIC_LOCATION = "static"
    AWS_MEDIA_LOCATION = "media"
    AWS_QUERYSTRING_AUTH = False
    
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
    STATIC_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/{AWS_STATIC_LOCATION}/"
    STATICFILES_STORAGE = "apps.common.storage_backends.StaticStorage"
    MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/{AWS_MEDIA_LOCATION}/"
    DEFAULT_FILE_STORAGE = "apps.common.storage_backends.PublicMediaStorage"

# Email settings (you might want to move these from local.py)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = os.environ.get("EMAIL_PORT", 587)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# When running in a DigitalOcean app, Django sits behind a proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # Services
        'apps.portal.services.ai_services': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.portal.services.portal_services': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.portal.services.product_tree_services': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Views
        'apps.portal.views.agreement': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.portal.views.base': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.portal.views.organisation': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.portal.views.product_tree': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.portal.views.product': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.portal.views.work': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Root logger for catching any missed logs
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
