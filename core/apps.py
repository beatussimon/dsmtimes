from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        import core.signals  # Ensure signals are imported
        import core.templatetags.article_tags  # Import template tags for regex_replace