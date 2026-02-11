from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking, Bike


@receiver(post_save, sender=Booking)
def update_bike_availability(sender, instance, created, **kwargs):
    """
    When a booking is created or updated with status 'Active',
    set the related bike's availability to False.
    """
    if instance.status == 'Active':
        bike = instance.bike
        bike.is_available = False
        bike.save()