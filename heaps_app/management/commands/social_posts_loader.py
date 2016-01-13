from django.core.management.base import BaseCommand
from django.db import IntegrityError
from heaps_app import social_workers, models
from urlparse import urlparse


class Command(BaseCommand):
    def handle(self, *args, **options):
        # celebrities = [models.Celebrity.objects.get(pk=17)]  # PewDiePie - 17 Garrix - 42 PAVEL VOLYA - 38
        celebrities = models.Celebrity.objects.all()

        for celebrity in celebrities:
            # Get celebrity all social networks
            social_networks = celebrity.socialnetwork_set.all()

            for social_network in social_networks:
                # Check if social_workers module exists social network worker class
                worker_class = '{}Worker'.format(social_network.social_network.capitalize())

                if hasattr(social_workers, worker_class):
                    url_info = urlparse(social_network.url)

                    worker = getattr(social_workers, worker_class)(url_info.path.strip('/'))
                    related_model = getattr(celebrity, 'celebrity_{}_posts'.format(social_network.social_network))

                    posts = worker.get_posts()

                    for post in posts:
                        try:
                            related_model.create(**post)
                        except IntegrityError:
                            break
