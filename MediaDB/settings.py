"""
Django settings for MediaDB project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'pwsjl=-e%$lp3s^+ja7r$ik3ynf@2551v(m0bmjm0u1fy(9d)r'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG')
ALLOWED_HOSTS = ['127.0.0.1', 'themediadb.herokuapp.com']


# Application definition
INSTALLED_APPS = [
    'media.apps.MediaConfig',
    'users.apps.UsersConfig',
    'crispy_forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'import_export',
    'rest_framework',
    'storages',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'MediaDB.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],

            'libraries':{
                'media_tags': 'media.templatetags.media_tags',
            }
        },
    },
]

WSGI_APPLICATION = 'MediaDB.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


#STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'resources')
MEDIA_URL = '/resources/'

#-----------------------------------------------------------------------------------------------------#

CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGIN_REDIRECT_URL = 'media-home'

LOGIN_URL = 'login'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES' :('rest_framework.permissions.IsAuthenticatedOrReadOnly',)
    #'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdmin',)
}

#-----------------------------------------------------------------------------------------------------#

#AWS S3 Bucket Settings from Environmental Variables

AWS_ACCESS_KEY_ID = "AKIA3PZJAERXYJ7FQSV4"
AWS_SECRET_ACCESS_KEY = "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"
AWS_STORAGE_BUCKET_NAME = "mediadb-bucket"
AWS_DEFAULT_REGION = "us-west-2"
AWS_REGION_NAME = "us-west-2"

AWS_QUERYSTRING_AUTH = False
AWS_S3_OVERWRITE = False
AWS_DEFAULT_ACL = None

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

#AWS Bucket Settings for Static Files
STATIC_URL = 'https://mediadb-bucket.s3-us-west-2.amazonaws.com/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'media/static')]
STATIC_ROOT = 'https://mediadb-bucket.s3-us-west-2.amazonaws.com/media'

STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
