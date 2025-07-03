from django.conf import settings
from .models import Category

def vtshop_context(request):
    return {
        # Cơ bản
        'SITE_NAME': settings.SITE_NAME,
        'SITE_DOMAIN': settings.SITE_DOMAIN,
        'SITE_DESCRIPTION': settings.SITE_DESCRIPTION,
        'SITE_KEYWORDS': settings.SITE_KEYWORDS,
        'SITE_AUTHOR': settings.SITE_AUTHOR,
        'SITE_VERSION': settings.SITE_VERSION,
        'STATIC_VERSION': settings.SITE_VERSION,

        # Mạng xã hội / SEO
        'META_OG_TITLE': settings.META_OG_TITLE,
        'META_OG_DESCRIPTION': settings.META_OG_DESCRIPTION,
        'META_OG_IMAGE': settings.META_OG_IMAGE,
        'META_TWITTER_HANDLE': settings.META_TWITTER_HANDLE,

        # Thương hiệu
        'BRAND_NAME': settings.BRAND_NAME,
        'BRAND_SLOGAN': settings.BRAND_SLOGAN,
        'BRAND_EMAIL': settings.BRAND_EMAIL,

        # Google Analytics
        'GA_TRACKING_ID': settings.GA_TRACKING_ID,

    }

def categories_processor(request):
    return {
        'header_categories': Category.objects.all()
    }
