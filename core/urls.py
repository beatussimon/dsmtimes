# dsmtimes/urls.py
from django.urls import path, include
from core import views
from core.admin import dsm_admin_site
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', dsm_admin_site.urls),
    path('', views.home, name='home'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('submit-article/', views.submit_article, name='submit_article'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('profile/', views.profile, name='profile'),
    path('profile/<str:username>/', views.public_profile, name='public_profile'),
    path('newsletter-signup/', views.newsletter_signup, name='newsletter_signup'),
    path('search/', views.search, name='search'),
    path('toggle-dark-mode/', views.toggle_dark_mode, name='toggle_dark_mode'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name='register'),
    path('accounts/logout/', views.custom_logout, name='logout'),
    path('live/', views.live_updates, name='live_updates'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('chief-editor/', views.custom_admin, name='custom_admin'),
    path('faq/', views.faq, name='faq'),
    path('feedback/', views.feedback, name='feedback'),
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_post_detail, name='blog_post_detail'),
    path('custom-logout', views.custom_logout, name='custom_logout')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)