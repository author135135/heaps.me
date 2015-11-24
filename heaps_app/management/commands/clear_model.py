from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--model', nargs='+', type=str)

    def handle(self, *args, **options):
        if options['model']:
            for model_name in options['model']:
                try:
                    model = apps.get_model('heaps_app', model_name)
                except LookupError:
                    continue

                model.objects.all().delete()
