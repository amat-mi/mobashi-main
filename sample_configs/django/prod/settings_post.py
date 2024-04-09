# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

import os
from django.conf import settings

with open(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                       os.getenv('PUBLIC_PGP_KEY_PATH', '../django_secrets/public.key')))) as f:
    PUBLIC_PGP_KEY = f.read().strip()

with open(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                       os.getenv('PRIVATE_PGP_KEY_PATH', '../django_secrets/private.key')))) as f:
    PRIVATE_PGP_KEY = f.read().strip()

with open(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                       os.getenv('DJANGO_DATABASE_PASSWORD_FILE', '../django_secrets/password.txt')))) as f:
    DJANGO_DATABASE_PASSWORD = f.read().strip()

DATABASES = {
    "default": {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DJANGO_DATABASE_NAME'),
        'USER': os.getenv('DJANGO_DATABASE_USER'),
        'PASSWORD': DJANGO_DATABASE_PASSWORD,
        'HOST': os.getenv('DJANGO_DATABASE_HOST'),
        'PORT': os.getenv('DJANGO_DATABASE_PORT'),
    },
    "milano": {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'milano',
        'USER': os.getenv('DJANGO_DATABASE_USER'),
        'PASSWORD': DJANGO_DATABASE_PASSWORD,
        'HOST': os.getenv('DJANGO_DATABASE_HOST'),
        'PORT': os.getenv('DJANGO_DATABASE_PORT'),
    }
}

settings.DJOSER['PASSWORD_RESET_CONFIRM_URL'] = 'ui/login/password-reset/{uid}/{token}'

settings.DJOSER['WEBAUTHN'] = {
    'RP_NAME': "Mobashi MAIN",
    'RP_ID': 'localhost',
    'ORIGIN': [
        "http://localhost:4100",
        "https://localhost:4100",
    ]
}

settings.HUEY['immediate'] = False
settings.HUEY['consumer']['workers'] = 4
settings.HUEY['filename'] = '/sqlitehuey/sqlitehuey.db'

# ROUT

ROUT_CONFIG = {
    'SERVER_URL': 'http://localhost:4001',
    'DBALIAS': 'milano',            #leave commented to NOT create actual routing
    'K': 1,                         #number of alternative route to generate (suggested 1..4)
    #'FOONETWORK': 'FOO'            #leave commented to NOT create straight line Traits
}

# SURV

SURV_CONFIG = {
    'SERVER_URL': 'http://host.docker.internal:4002',
    'CLIENT_URL': 'http://localhost:4102',
}

# HARVESTING

# See Python Huey docs.
# If 'RETRIES' or 'RETRY_DELAY missing or 0, they won't be used.
# If 'CRONTAB' missing or nothing set, disable periodic Harvesting altogether.

HARVESTING_TASK = {
    'RETRIES': 0,
    'RETRY_DELAY': 0,
    'CRONTAB': {
        'MONTH': None,
        'DAY': None,
        'DAY_OF_WEEK': None,
        'HOUR': None,
        'MINUTE': None
    }
}

# SYNCING

# See Python Huey docs.
# If 'RETRIES' or 'RETRY_DELAY missing or 0, they won't be used.

SYNCING_TASK = {
    'RETRIES': 0,
    'RETRY_DELAY': 0
}

# ROUTING

# See Python Huey docs.
# If 'RETRIES' or 'RETRY_DELAY missing or 0, they won't be used.

ROUTING_TASK = {
    'RETRIES': 0,
    'RETRY_DELAY': 0
}
