from pathlib import Path
from decouple import config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY =  config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool) #True


# Application definition

INSTALLED_APPS = [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    
    # 'channels',
    'chat',
    'daphne',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'profiles',
    'appadmin',
    'category',
    'store',
    'carts',
    'orders',
    'blog',
    # 'admin_honeypot',
    'storages',
    'django_ckeditor_5',
    'mptt',
    'warehouse',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django_session_timeout.middleware.SessionTimeoutMiddleware',#session timeout
    'allauth.account.middleware.AccountMiddleware', # allauth

]

#session timeout
# SESSION_EXPIRE_SECONDS = 3600  # 1 hour
# SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
# SESSION_TIMEOUT_REDIRECT = 'accounts/login'


ROOT_URLCONF = 'projectCart.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'category.context_processors.category_links',
                'carts.context_processors.counter',

                'chat.context_processors.room_links',
            ],
        },
    },
]

WSGI_APPLICATION = 'projectCart.wsgi.application'
#Dephne / Chat
ASGI_APPLICATION = "projectCart.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}


AUTH_USER_MODEL = 'profiles.Account'

# allauth settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        #'KEY': config('GOOGLE_CLIENT_ID'),
        #'SECRET': config('GOOGLE_CLIENT_SECRET'),
        'SCOPE': ['email', 'profile'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR / 'static')
STATICFILES_DIRS = [
    os.path.join('projectCart/static'),
]

# AWS S3 Static Files Configuration
# AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
# AWS_S3_OBJECT_PARAMETERS = {
#     'CacheControl': 'max-age=86400',
# }
# AWS_S3_REGION_NAME = 'us-west-2',
# AWS_S3_FILE_OVERWRITE = False
# AWS_DEFAULT_ACL = 'public-read'
# AWS_LOCATION = 'static'
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static')
# ]
# STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


# media File Configuration
# DEFAULT_FILE_STORAGE = 'projectCart.media_storages.MediaStorage'
MEDIA_URL = '/media/'
# MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SMTP configuration / email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_HOST = config('EMAIL_HOST')
# EMAIL_PORT = config('EMAIL_PORT', cast=int)
# EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
# EMAIL_HOST_USER = config('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = ('EMAIL_HOST_PASSWORD')

#midtrans key used to identify Settings
MIDTRANS = {
    'MERCHANT_ID': config('MIDTRANS_MERCHANT_ID'),
    'SERVER_KEY': config('MIDTRANS_SERVER_KEY'),
    'CLIENT_KEY': config('MIDTRANS_CLIENT_KEY')
}

# Raja Onkir setings
RAJA_ONGKIR_KEY = config('RAJA_ONGKIR_KEY')

# tag masses settings
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

# Ckeditor_5
customColorPalette = [
        {
            'color': 'hsl(4, 90%, 58%)',
            'label': 'Red'
        },
        {
            'color': 'hsl(340, 82%, 52%)',
            'label': 'Pink'
        },
        {
            'color': 'hsl(291, 64%, 42%)',
            'label': 'Purple'
        },
        {
            'color': 'hsl(262, 52%, 47%)',
            'label': 'Deep Purple'
        },
        {
            'color': 'hsl(231, 48%, 48%)',
            'label': 'Indigo'
        },
        {
            'color': 'hsl(207, 90%, 54%)',
            'label': 'Blue'
        },
    ]

#CKEDITOR_5_CUSTOM_CSS = 'path_to.css' # optional
#CKEDITOR_5_FILE_STORAGE = "store.ckeditor5.CustomStorage" # optional
#CK_EDITOR_5_UPLOAD_FILE_VIEW_NAME = "media.ckeditor5"
#CKEDITOR_5_ALLOW_ALL_FILE_TYPES = True
#CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'pdf', 'png', 'jpg'] # optional
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', ],

    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
        'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 
                    'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable',],
        
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
            'tableProperties', 'tableCellProperties' ],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading' : {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}