from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'araincdb',
#         'USER': 'arainc',
#         'PASSWORD': 'arainc@123',
#         'HOST': 'localhost',
#         # 'HOST': '208.115.109.194',
#         'PORT': '3306',
#           'OPTIONS': {
#           'charset' : 'utf8mb4',
#           'use_unicode' : True,
#           'sql_mode': 'NO_ENGINE_SUBSTITUTION'
#         },
#     }
# }



