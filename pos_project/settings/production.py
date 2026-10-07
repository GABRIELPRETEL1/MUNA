from .base import *

# Validate production-only settings before Django starts. Base settings retain
# their development-friendly defaults for local use.
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('DJANGO_SECRET_KEY must be set to a non-empty value in production.')

ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '').split(',') if host.strip()]
if not ALLOWED_HOSTS:
    raise ValueError('ALLOWED_HOSTS must contain at least one hostname in production.')
if '*' in ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must not contain '*' in production.")

DEBUG = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'pos_db'),
        'USER': os.getenv('POSTGRES_USER', 'pos_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'pos_password'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}
