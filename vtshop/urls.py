from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('filer/', include('filer.urls')),
    path('admin/', admin.site.urls),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path('', include('store.urls')),
]

handler404 = 'store.views.custom_404_view'
