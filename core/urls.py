# dsmtimes/urls.py
from django.contrib import admin
from django.urls import path, include
from core import views
from core.admin import dsm_admin_site  # Import custom admin site here
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', dsm_admin_site.urls),  # Use custom admin site
    path('', views.home, name='home'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('submit-article/', views.submit_article, name='submit_article'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('profile/', views.profile, name='profile'),
    path('newsletter-signup/', views.newsletter_signup, name='newsletter_signup'),
    path('search/', views.search, name='search'),
    path('toggle-dark-mode/', views.toggle_dark_mode, name='toggle_dark_mode'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)