# dsmtimes/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('core.urls')),  # Include core URLs at root
    path('accounts/', include('django.contrib.auth.urls')),  # Keep auth URLs separate
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)