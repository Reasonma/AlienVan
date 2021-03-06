"""
Django settings for alienVan project.

Generated by 'django-admin startproject' using Django 2.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5n=1kd%sqn5-&y9v3s#rebx%vhe1ahv=vgwb*q&^-2vqmy48of'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'celery',   # 任务队列
    'django_celery_results',    # django 任务队列拓展
    'index',
    'management',

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

ROOT_URLCONF = 'alienVan.urls'


CONTEXT_PROCESSORS = [
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [],
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': CONTEXT_PROCESSORS,
        },
    },
]

WSGI_APPLICATION = 'alienVan.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

# 静态文件部署根目录
STATIC_ROOT = '/www/wwwroot/pan.zzuliacgn.com/alienVan/static/'

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

MEDIA_URL = '/tempFiles/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'tempFiles')

#############################
# celery 配置信息 start
#############################
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
# result_backend = 'django-db'
CELERY_RESULT_BACKEND = 'django-db' # 如果使用django-celery-results 則 CELERY_RESULT_BACKEND
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
# from celery.schedules import crontab
# from celery.schedules import timedelta

# CELERYBEAT_SCHEDULE = {    #定时器策略
#     #定时任务一：　每隔30s运行一次
#     u'测试定时器1': {
#         "task": "art.tasks.tsend_email",
#         #"schedule": crontab(minute='*/2'),  # or 'schedule':   timedelta(seconds=3),
#         "schedule":timedelta(seconds=30),
#         "args": (),
#     },
# }
#############################
# celery 配置信息 end
#############################