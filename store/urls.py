from django.urls import path
from . import views
from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home_view, name='home'),
    path('product/<slug:slug>/', views.product_view, name='product'),
    path('products/', views.products_view, name='products'),
    path('cart/', views.cart_view, name='cart'),
    path('get/variant/<int:variant_id>/', views.get_variant, name='get_variant'),
    path('sitemap.xml', sitemap, {'sitemaps': {
        'products': views.ProductSitemap,
    }}, name='sitemap'),
    path("robots.txt", views.robots_txt),
    path('order/submit/', views.submit_cart_order, name="order_submit")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)