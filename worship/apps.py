from django.apps import AppConfig


class WorshipConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'worship'
    
    def ready(self):
        import worship.tasks  # Ensure tasks are discovered
