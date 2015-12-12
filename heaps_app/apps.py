from django.apps import AppConfig


class HeapsAppConfig(AppConfig):

    name = 'heaps_app'
    verbose_name = 'Heaps App'

    def ready(self):
        import heaps_app.signals.handlers
