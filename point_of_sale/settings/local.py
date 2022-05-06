from .base import *


DEBUG = True

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

'''LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}
'''