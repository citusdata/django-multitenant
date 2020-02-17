from .settings import *

DATABASES = {
    "default": {
        'ENGINE': 'django_multitenant.backends.postgresql',
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": 5604,
        "TEST": {
            "NAME": "postgres",
            "SERIALIZE": False
        }
    }
}


USE_CITUS = False
