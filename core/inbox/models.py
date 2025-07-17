from django.db import models
from accounts.models import User, Ewaste

# Create your models here.
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class Offer(models.Model):
    message = models.OneToOneField(Message, on_delete=models.CASCADE, related_name='offer')
    ewaste = models.ForeignKey(Ewaste, on_delete=models.CASCADE)
    eco_points = models.PositiveIntegerField()
    offer_type = models.CharField(max_length=20, choices=[('user', 'User'), ('authority', 'Authority')])
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
