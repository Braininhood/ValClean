from django.apps import AppConfig


class CalendarSyncConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calendar_sync'
    
    def ready(self):
        """Import signals when app is ready."""
        import calendar_sync.signals  # noqa