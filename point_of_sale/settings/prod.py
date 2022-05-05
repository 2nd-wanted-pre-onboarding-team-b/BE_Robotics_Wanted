from .base import *


DEBUG = False

SECRET_KEY = get_secret("SECRET_KEY")

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'db_pos',
        'USER': 'root',
        'PASSWORD': get_secret("MYSQL_LOCAL_PASSWORD"),
        'HOST': 'localhost',
        'PORT': 3306
    }
}