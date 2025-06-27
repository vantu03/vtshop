from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home_view, name='home'),
    path('product/<slug:slug>/', views.product_view, name='product'),
    path('products/', views.products_view, name='products'),
    path('cart/', views.cart_view, name='cart'),
    path('get/variant/<int:variant_id>/', views.get_variant, name='get_variant'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)