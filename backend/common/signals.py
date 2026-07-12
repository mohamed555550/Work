from django.db.models.signals import pre_save
from django.dispatch import receiver

from .media import optimize_model_images


@receiver(pre_save, dispatch_uid='common.optimize_uploaded_images')
def optimize_uploaded_images(sender, instance, raw=False, **kwargs):
    if raw or not hasattr(instance, '_meta'):
        return
    optimize_model_images(instance)
