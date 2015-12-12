import os
from django.db.models.signals import pre_save
from django.dispatch import receiver
from heaps_app import models


@receiver(pre_save, sender=models.User)
def user_pre_save_handler(sender, instance, raw, using, update_fields, **kwargs):
    # Delete old user avatar image
    if instance.pk is not None:
        user = models.User.objects.get(pk=instance.pk)

        if os.path.basename(user.avatar.path) != os.path.basename(instance.avatar.path):
            os.remove(user.avatar.path)
