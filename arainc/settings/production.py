from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['iog.araincbd.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
	'OPTIONS': {
	'read_default_file':'/home/ubuntu/arainc/auth/mysql.cnf'
	},
    }
}
