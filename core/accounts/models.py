from django.db import models
from django.contrib.auth.models import User


# Create your models here.

STATUS_CHOICES = [
    ('submitted', 'Submitted'),
    ('approved', 'Approved'),
    ('awaiting_drop', 'Awaiting Drop'),
    ('received', 'Received'),
    ('rejected', 'Rejected'),
    ('rewarded', 'Rewarded'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class Ewaste(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='ewaste/')
    description = models.TextField()
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    awarded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='given_points')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    drop_location = models.ForeignKey('DropCenter', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.title} by {self.user.username}"
    

class EcoPoint(models.Model):
    ewaste = models.OneToOneField(Ewaste, on_delete=models.CASCADE, related_name="eco_point")
    points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.points} points for {self.ewaste.title}"

class DropCenter(models.Model):
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.area}, {self.city}"
    
# accounts/views.py

from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from .models import EcoPoint

from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from .models import UserProfile

class LeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = (
            User.objects
            .annotate(total_points=Sum('ewaste__eco_point__points'))
            .filter(total_points__gt=0)
            .order_by('-total_points')[:10]
        )

        leaderboard = []
        for user in users:
            profile = getattr(user, 'userprofile', None)
            leaderboard.append({
                "username": user.username,
                "eco_points": user.total_points or 0,
                "profile_pic": profile.profile_pic.url if profile and profile.profile_pic else None
            })

        return Response(leaderboard)
    
class Reward(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    eco_points_required = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='reward_images/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.eco_points_required} pts)"

class EcoPointTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ewaste = models.ForeignKey(Ewaste, on_delete=models.SET_NULL, null=True, blank=True)
    points = models.IntegerField()  # positive = earn, negative = spend
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.points} pts by {self.user.username} for {self.reason}"

# models.py
class UserReward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} redeemed {self.reward.name}"


class Notification(models.Model):
    NOTIF_TYPE = [
        ('status',   'Status Update'),
        ('points',   'Eco‑Points Awarded'),
        # add more types if you need
    ]
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    ewaste      = models.ForeignKey(Ewaste, on_delete=models.CASCADE, null=True, blank=True)
    notif_type  = models.CharField(max_length=20, choices=NOTIF_TYPE)
    message     = models.TextField()
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notif_type_display()} to {self.user.username}"
