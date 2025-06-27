from pathlib import Path
from decouple import config
import dj_database_url

# ========== Paths ==========
BASE_DIR = Path(__file__).resolve().parent.parent

# ========== Django cơ bản ==========
DEBUG = config('DEBUG', cast=bool, default=False)
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(',')

# ========== SEO / Website Info ==========
SITE_NAME = config('SITE_NAME')
SITE_DOMAIN = config('SITE_DOMAIN')
SITE_DESCRIPTION = config('SITE_DESCRIPTION')
SITE_KEYWORDS = config('SITE_KEYWORDS')
SITE_AUTHOR = config('SITE_AUTHOR')

# ========== Mạng xã hội / Metadata ==========
META_OG_TITLE = config('META_OG_TITLE')
META_OG_DESCRIPTION = config('META_OG_DESCRIPTION')
META_TWITTER_HANDLE = config('META_TWITTER_HANDLE')

# ========== Thương hiệu ==========
BRAND_NAME = config('BRAND_NAME')
BRAND_SLOGAN = config('BRAND_SLOGAN')

# ========== Google Analytics ==========
GA_TRACKING_ID = config('GA_TRACKING_ID', default='')

# ========== Email ==========
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)

# ========== Ứng dụng ==========
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
]

# ========== Middleware ==========
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ========== URL và WSGI ==========
ROOT_URLCONF = 'vtshop.urls'
WSGI_APPLICATION = 'vtshop.wsgi.application'

# ========== Template ==========
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.vtshop_context',
            ],
        },
    },
]

# ========== Cơ sở dữ liệu ==========
DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}

# ========== Xác thực ==========
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

# ========== Quốc tế hóa ==========
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ========== Static ==========
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = '/upload/'
MEDIA_ROOT = BASE_DIR / 'upload'

# ========== Primary Key ==========
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
