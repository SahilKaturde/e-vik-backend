# inbox/serializers.py
from rest_framework import serializers
from .models import Offer
from accounts.models import Ewaste
from accounts.serializers import UserSerializer

class EwasteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ewaste
        fields = ['id', 'title', 'image', 'description']

class OfferSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    recipient = UserSerializer()
    ewaste = EwasteSerializer()
    created_at = serializers.DateTimeField(format="%b %d, %Y %H:%M")
    offer_type = serializers.SerializerMethodField()
    
    class Meta:
        model = Offer
        fields = [
            'id', 
            'sender', 
            'recipient', 
            'ewaste', 
            'eco_points', 
            'offer_type', 
            'status', 
            'created_at'
        ]
    
    def get_offer_type(self, obj):
        if obj.message.recipient == self.context['request'].user:
            return 'received'
        elif obj.message.sender == self.context['request'].user:
            return 'sent'
        elif obj.offer_type == 'authority':
            return 'authority'
        return 'other'