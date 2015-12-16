from django.core.management.base import BaseCommand, CommandError
from django.apps import apps


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--models', nargs='+', type=str)

    def handle(self, *args, **options):
        models = options.get('models')

        if models:

            for model_name in models:
                try:
                    model = apps.get_model(app_label=model_name)
                except LookupError:
                    continue

                model.objects.all().delete()
        else:
            raise CommandError("Missing argument --models required")
