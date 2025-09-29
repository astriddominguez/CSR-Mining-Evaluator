import os
from decouple import config
from unipath import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Directori arrel del projecte 
PROJECT_DIR = Path(__file__).parent # Directori del projecte (on es troba el fitxer settings.py)

# Clau secreta: pendent crear SECRET_KEY desde el fitxer.env !
# Es fa servir per firmar cookies, protegir contrasenyes i encriptar informació sensible.
SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_1122')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False # Producció -> False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'astrid2025.pythonanywhere.com'] # Producció únicament astrid2025.pythonanywhere.com

# Definició d'aplicacions
INSTALLED_APPS = [
    'django.contrib.admin', # Activa el panell d'administració de Django (ADMIN) - Doc: https://docs.djangoproject.com/en/5.2/ref/contrib/admin/ 
    'django.contrib.auth', # Dependencia de django.contrib.admin
    'django.contrib.contenttypes', # Dependencia de django.contrib.admin
    'django.contrib.sessions', # Dependencia de django.contrib.admin
    'django.contrib.messages', # Dependencia de django.contrib.admin
    'django.contrib.staticfiles', # Gestió d'arxius estàtics - Doc: https://docs.djangoproject.com/en/5.2/howto/static-files/ 
    'processdata', # aplicació pròpia
    #'django.contrib.humanize', 
    'django_extensions' # en aquest projecte es fa servir per crear gràfics dels models automàticament.
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', # permet activar mesures de seguretat amb facilitat
    'django.contrib.sessions.middleware.SessionMiddleware', # Requeriment d'admin
    'django.middleware.common.CommonMiddleware', # Afegeix funcionalitats bàsiques a nivell de routing i capçeleres
    'django.middleware.csrf.CsrfViewMiddleware', # Analitza si la petició és POST i valida el token CSRF.
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Requeriment d'admin
    'django.contrib.messages.middleware.MessageMiddleware', # Requeriment d'admin
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # protegeix la web contra atacs de 'clickjacking'
    'whitenoise.middleware.WhiteNoiseMiddleware', # permet servir fitxers estàtics en producció (amb collecstatic)
]

ROOT_URLCONF = 'core.urls' # Li diu a Django on ha de buscar les rutes
TEMPLATE_DIR = os.path.join(BASE_DIR, "core/templates")  # Arrel de les vistes (html)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates', # Motor de plantilles de Django
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug', # proporciona informació útil durant el desenvolupament (debug=True)
                'django.template.context_processors.request', # requeriment d'admin
                'django.contrib.auth.context_processors.auth', # requeriment d'admin
                'django.contrib.messages.context_processors.messages', # requeriment d'admin
            ],
            'libraries': {

            }
        },

    },
]

# Directori de metadades incloses en JSON
JSON_DIR = os.path.join(BASE_DIR, "processdata/config")  

# Referència al punt d'entrada
WSGI_APPLICATION = 'core.wsgi.application'

# Base de Dades
# https://docs.djangoproject.com/en/5.2/ref/databases/
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Validador de contrasenyes
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators (es fa servir al panell d'administrador)

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

# Internacionalització
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-es' # en-us o ca 
TIME_ZONE = 'Europe/Madrid' # UTC
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Fitxers estàtics (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Busca fitxers estàtics dins de core/static
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'core/static'),
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,  # Mantenir els loggers que venen per defecte
    "formatters": { # format de com es veurán els missatges al terminal
        "verbose": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        },
        "simple": {
            "format": "%(levelname)s | %(message)s"
        },
    },
    "handlers": { # on s'envia el missatge
        "console": {
            "class": "logging.StreamHandler", # mostra per pantalla
            "formatter": "verbose"
        },
    },
    "root": { # logger global per defecte
        "handlers": ["console"],
        "level": "DEBUG",  
    },
    "loggers": { # loggers especifics per a moduls concrets.
        "django": {
            "handlers": ["console"],
            "level": "WARNING",  
            "propagate": False,
        },
        "processdata": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# a partir de django 3.2 es recomana que totes les claus primàries siguin de 64 bits. (Afegit despres de la migració a Django 5.2.2)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
