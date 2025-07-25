from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile,Ewaste,Reward
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'ewaste', 'notif_type', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    address = serializers.CharField(write_only=True, required=False)
    profile_pic = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'address', 'profile_pic']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        address = validated_data.pop('address', '')
        profile_pic = validated_data.pop('profile_pic', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        UserProfile.objects.create(user=user, address=address, profile_pic=profile_pic)
        return user


class EwasteSerializer(serializers.ModelSerializer):
    posted_by = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()
    points = serializers.SerializerMethodField()

    class Meta:
        model = Ewaste
        fields = [
            'id',
            'title',
            'image',
            'description',
            'address',
            'posted_by',
            'profile_pic',
            'status',
            'points',
        ]
        read_only_fields = ['user']

    def get_posted_by(self, obj):
        return obj.user.username

    def get_profile_pic(self, obj):
        try:
            request = self.context.get("request")
            if obj.user.userprofile.profile_pic:
                return request.build_absolute_uri(obj.user.userprofile.profile_pic.url)
        except:
            return None

    def get_points(self, obj):
        try:
            return obj.eco_point.points  # only works if EcoPoint exists
        except:
            return 0

class RewardSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Reward
        fields = ['id', 'name', 'description', 'eco_points_required', 'image']

# accounts/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Add other fields if needed
