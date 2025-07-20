from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Ewaste, Notification, EcoPoint

@receiver(post_save, sender=Ewaste)
def notify_status_change(sender, instance, created, **kwargs):
    if not created:
        Notification.objects.create(
            user=instance.user,
            ewaste=instance,
            notif_type='status',
            message=f"Your e‑waste “{instance.title}” is now {instance.get_status_display()}.",
        )

@receiver(post_save, sender=EcoPoint)
def notify_points_awarded(sender, instance, created, **kwargs):
    if created and instance.points > 0:
        Notification.objects.create(
            user=instance.ewaste.user,
            ewaste=instance.ewaste,
            notif_type='points',
            message=f"You earned {instance.points} Eco‑Points for “{instance.ewaste.title}”!",
        )
