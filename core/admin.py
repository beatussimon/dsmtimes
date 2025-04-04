# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from .models import Article, Category, SubscriptionPlan, Comment, NewsletterSubscription, UserProfile, Tag, ArticleMedia, FAQ, Feedback,BlogPost
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone

class DSMAdminSite(admin.AdminSite):
    site_header = "DSM Times Administration"
    site_title = "DSM Times Admin"
    index_title = "Welcome to DSM Times Admin"

dsm_admin_site = DSMAdminSite(name='dsm_admin')

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

class ArticleMediaInline(admin.TabularInline):
    model = ArticleMedia
    extra = 1

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'submitted_at', 'published_at', 'views_count', 'breaking_news')
    list_filter = ('status', 'category', 'is_premium', 'breaking_news')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ArticleMediaInline]
    actions = ['publish_articles']

    def publish_articles(self, request, queryset):
        queryset.update(status='published', published_at=timezone.now())
    publish_articles.short_description = "Publish selected articles"

dsm_admin_site.register(User, UserAdmin)
dsm_admin_site.register(Article, ArticleAdmin)
dsm_admin_site.register(Category)
dsm_admin_site.register(SubscriptionPlan)
dsm_admin_site.register(Comment)
dsm_admin_site.register(NewsletterSubscription)
dsm_admin_site.register(UserProfile)
dsm_admin_site.register(Tag)
dsm_admin_site.register(ArticleMedia)
dsm_admin_site.register(BlogPost)

@receiver(post_migrate)
def create_groups(sender, **kwargs):
    if sender.name == 'core':
        editor_group, _ = Group.objects.get_or_create(name='Editors')
        from django.contrib.auth.models import Permission
        editor_permissions = Permission.objects.filter(
            content_type__app_label='core',
            codename__in=['change_article', 'delete_article', 'add_article', 'change_comment', 'delete_comment', 'add_comment']
        )
        editor_group.permissions.set(editor_permissions)
        Group.objects.get_or_create(name='Subscribers')



class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'created_at', 'updated_at')
    list_editable = ('order',)  # Allow inline editing of order
    search_fields = ('question', 'answer')
    ordering = ('order', 'created_at')

dsm_admin_site.register(FAQ, FAQAdmin)  # Register the FAQ model

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_preview', 'submitted_at', 'is_resolved')
    list_filter = ('is_resolved', 'submitted_at')
    search_fields = ('message', 'user__username')
    list_editable = ('is_resolved',)  # Allow inline toggling of resolved status
    actions = ['mark_resolved']

    def message_preview(self, obj):
        return obj.message[:50] + ('...' if len(obj.message) > 50 else '')
    message_preview.short_description = 'Message'

    def mark_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
    mark_resolved.short_description = "Mark selected feedback as resolved"

dsm_admin_site.register(Feedback, FeedbackAdmin)  # Register the Feedback model