from pathlib import Path
import os
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("DEBUG", default=0))

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS").split(" ")
DJANGO_SUPERUSER_PASSWORD = os.environ.get("DJANGO_SUPERUSER_PASSWORD", 'P@ssw0rd123')

# Proxy Settings
HTTP_PROXY = os.environ.get("HTTP_PROXY", '')
HTTPS_PROXY = os.environ.get("HTTPS_PROXY", '')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IS_EXAM.settings.environment')

# Application definition

INSTALLED_APPS = [
    'main',
    "sslserver",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rosetta',
    'parler',
]

MIDDLEWARE = [
     # 'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

# ROSETTA (TRANSLATE CONTENT)
# What language you want. You should iso codes for language codes.
# You can find iso codes in here.
LANGUAGES = [
    ('uk', _('Ukraine')),
    ('en', _('English')),
]
# Rosetta store the translation datas in this file.
#LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)
LOCALE_PATHS = [
    (os.path.join(BASE_DIR, "locale"))
]

ROSETTA_SHOW_AT_ADMIN_PANEL = True
ROSETTA_REVERSE_URL = 'exams'

# PARLERER
PARLER_LANGUAGES = {
    None: (
        {'code': 'uk',}, # English
        {'code': 'en',}, # French
    ),
    'default': {
        'fallbacks': ['uk'],
        'hide_untranslated': False,
    }
}

ROOT_URLCONF = 'IS_EXAM.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],

        },
    },
]

WSGI_APPLICATION = 'IS_EXAM.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get("PSQL_DATABASE"),
        'USER': os.environ.get("PSQL_USER"),
        'PASSWORD': os.environ.get("PSQL_PASSWORD"),
        'HOST': os.environ.get("PSQL_HOST"),
        'PORT': os.environ.get("PSQL_PORT", "5432"),
    }
}

#AAD
LOGIN_URL = '/oauth2/login'

#Local
#LOGIN_URL = '/accounts/login/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'

AUTH_USER_MODEL = "main.AditionalUserInfo"

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = '/static/'
#STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_ADFS = {
    'AUDIENCE': os.environ.get("CLIENT_ID", "7444c7da-fe5b-4894-8348-702227048844"),
    'CLIENT_ID': os.environ.get("CLIENT_ID", "7444c7da-fe5b-4894-8348-702227048844"),
    'CLIENT_SECRET': os.environ.get("CLIENT_SECRET", "iQj8Q~TXZx~KWG.zIk_osGDT91Wq2pkDA2KcTa2_"),
    'PROXIES': {
                'http': HTTP_PROXY,
                'https': HTTPS_PROXY
               },
    'CLAIM_MAPPING': {
                      'first_name': 'given_name',
                      'last_name': 'family_name',
                      'email': 'upn'
                      },
    'GROUPS_CLAIM': 'roles',
    'MIRROR_GROUPS': True,
    'USERNAME_CLAIM': 'upn',
    'TENANT_ID': os.environ.get("TENANT_ID", "ea631a26-6dd8-4571-a85f-ebeda50d5724"),
    'RELYING_PARTY_ID': os.environ.get("CLIENT_ID", "7444c7da-fe5b-4894-8348-702227048844"),
}

# LOGGING
LOGGING = {
    'version': 1,
    # The version number of our log
    'disable_existing_loggers': False,
    # django uses some of its own loggers for internal operations. In case you want to disable them just replace the False above with true.
    # A handler for WARNING. It is basically writing the WARNING messages into a file called WARNING.log
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
        },
    },
    # A logger for WARNING which has a handler called 'file'. A logger can have multiple handler
    'loggers': {
       # notice the blank '', Usually you would put built in loggers like django or root here based on your needs
        '': {
            'handlers': ['file'], #notice how file variable is called in handler which has been defined above
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
