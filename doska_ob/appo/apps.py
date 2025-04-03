from django.apps import AppConfig


class AppoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appo'

    def ready(self):
        import appo.signals