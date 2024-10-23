
from .core import *

ALLOWED_HOSTS = ['.vercel.app', '*', ]

# Configure your production database 
# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# if 'RDS_DB_NAME' in os.environ:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.postgresql',
#             'NAME': os.environ['RDS_DB_NAME'],
#             'USER': os.environ['RDS_USERNAME'],
#             'PASSWORD': os.environ['RDS_PASSWORD'],
#             'HOST': os.environ['RDS_HOSTNAME'],
#             'PORT': os.environ['RDS_PORT'],
#         }
#     }
# else:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': BASE_DIR / 'db.sqlite3',
#         }
#    }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'base_rasyiid',
        'USER': 'mhddanny1',
        'PASSWORD': '@sukses123',
        # 'HOST': 'project.cct7dqrpfmm5.us-west-2.rds.amazonaws.com',
        'PORT': '5432',
    }
}

# Static and media files settings for production


DISABLE_SERVER_SIDE_CURSORS = True

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_PRELOAD = True

DOMAIN = "https://django-ecommerces.vercel.app"
CSRF_TRUSTED_ORIGINS = [
    #'https://django-ecommerces.vercel.app', 
    # 'ec2-35-166-148-8.us-west-2.compute.amazonaws.com',
    'https://0afc-112-215-245-68.ngrok-free.app',
    '*',
    ]


