# inbox/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Offer
from accounts.models import Ewaste, EcoPointTransaction
from .serializer import OfferSerializer

class UserOffersView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        offers = Offer.objects.filter(
            receiver=request.user
        ).select_related('sender', 'receiver', 'ewaste')
        
        serializer = OfferSerializer(offers, many=True, context={'request': request})
        return Response(serializer.data)

class AcceptOfferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, offer_id):
        offer = get_object_or_404(Offer, id=offer_id, receiver=request.user, status='pending')
        ewaste = offer.ewaste
        
        # Create transaction
        EcoPointTransaction.objects.create(
            user=request.user,
            ewaste=ewaste,
            points=offer.points_offered,
            reason=f"Offer accepted from {offer.sender.username}"
        )
        
        # Update offer and ewaste status
        offer.status = 'accepted'
        offer.save()
        
        ewaste.status = 'rewarded'
        ewaste.save()
        
        return Response({"message": "Offer accepted successfully."})

class RejectOfferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, offer_id):
        offer = get_object_or_404(Offer, id=offer_id, receiver=request.user, status='pending')
        offer.status = 'rejected'
        offer.save()
        return Response({"message": "Offer rejected successfully."})

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Offer  # Assuming you have an Offer model
from .serializer import OfferSerializer  # You need to define this serializer

class SendOfferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OfferSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
