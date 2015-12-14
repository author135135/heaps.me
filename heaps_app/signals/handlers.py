import os
from django.db.models import signals
from django.dispatch import receiver
from heaps_app import models


@receiver(signals.post_delete, sender=models.User)
def user_post_delete_handler(sender, instance=None, **kwargs):
    if (instance.avatar.field.default not in instance.avatar.path) and os.path.exists(instance.avatar.path):
        os.remove(instance.avatar.path)
