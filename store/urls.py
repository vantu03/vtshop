from django.urls import path
from . import views
from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home_view, name='home'),
    path('cart/', views.cart_view, name='cart'),
    path('get/variant/<int:variant_id>/', views.get_variant, name='get_variant'),
    path('sitemap.xml', sitemap, {'sitemaps': {
        'categories': views.CategorySitemap,
        'products': views.ProductSitemap,
    }}, name='sitemap'),
    path("robots.txt", views.robots_txt),
    path('order/submit/', views.submit_cart_order, name="order_submit"),
    path('review/submit/', views.submit_review, name='submit_review'),
    path('tim-kiem/', views.search_view, name='search'),
    path('<slug:category_slug>/<slug:product_slug>/', views.product_detail_view, name='product_detail'),
    path('<slug:category_slug>/', views.category_products_view, name='category_products'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)