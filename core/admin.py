# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from .models import Article, Category, SubscriptionPlan, Comment, NewsletterSubscription, UserProfile, Tag
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class DSMAdminSite(admin.AdminSite):
    site_header = "DSM Times Administration"
    site_title = "DSM Times Admin"
    index_title = "Welcome to DSM Times Admin"

dsm_admin_site = DSMAdminSite(name='dsm_admin')  # Custom admin site instance

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Re-register User with UserProfile inline on custom admin site
dsm_admin_site.register(User, UserAdmin)

# Register other models with the custom admin site
dsm_admin_site.register(Article)
dsm_admin_site.register(Category)
dsm_admin_site.register(SubscriptionPlan)
dsm_admin_site.register(Comment)
dsm_admin_site.register(NewsletterSubscription)
dsm_admin_site.register(UserProfile)
dsm_admin_site.register(Tag)

# Signal to create groups after migrations
@receiver(post_migrate)
def create_groups(sender, **kwargs):
    if sender.name == 'core':  # Only run for the 'core' app
        editor_group, _ = Group.objects.get_or_create(name='Editors')
        from django.contrib.auth.models import Permission
        editor_permissions = Permission.objects.filter(
            content_type__app_label='core',
            codename__in=['change_article', 'delete_article', 'add_article', 'change_comment', 'delete_comment', 'add_comment']
        )
        editor_group.permissions.set(editor_permissions)
        Group.objects.get_or_create(name='Subscribers')