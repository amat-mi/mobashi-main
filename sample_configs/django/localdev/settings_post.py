# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

import os
from django.conf import settings

with open(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                       os.getenv('DJANGO_DATABASE_PASSWORD_FILE')))) as f:
    DJANGO_DATABASE_PASSWORD = f.read().strip()

DATABASES = {
    "default": {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DJANGO_DATABASE_NAME'),
        'USER': os.getenv('DJANGO_DATABASE_USER'),
        'PASSWORD': DJANGO_DATABASE_PASSWORD,
        'HOST': 'db',  # use service name from docker-compose.yml
        'PORT': '5432',  # MUST use the "internal" service port, not the published one!!!
    },
    "milano": {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'milano',
        'USER': 'django',
        'PASSWORD': DJANGO_DATABASE_PASSWORD,
        'HOST': 'host.docker.internal',  # address of Docker Host machine
        'PORT': '5433',  # port on the Docker Host machine
    }
}

settings.DJOSER['PASSWORD_RESET_CONFIRM_URL'] = 'login/password-reset/{uid}/{token}'

settings.DJOSER['WEBAUTHN'] = {
    'RP_NAME': "Mobashi MAIN",
    'RP_ID': 'localhost',
    'ORIGIN': [
        "http://localhost:4100",
        "https://localhost:4100",
    ]
}

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
