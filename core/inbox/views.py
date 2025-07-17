from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

# Import your models from accounts
from accounts.models import Ewaste, EcoPointTransaction
from .models import Offer  # from inbox.models (same app)



# Create your views here.
class AcceptOfferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, offer_id):
        offer = get_object_or_404(Offer, id=offer_id, status='pending')
        ewaste = offer.ewaste
        if ewaste.user != request.user:
            return Response({"error": "You can't accept offers for others' e-waste."}, status=403)

        # Mark all other offers rejected
        Offer.objects.filter(ewaste=ewaste).exclude(id=offer.id).update(status='rejected')

        # Accept current offer
        offer.status = 'accepted'
        offer.save()

        # Award ecoPoints to uploader
        EcoPointTransaction.objects.create(
            user=ewaste.user,
            ewaste=ewaste,
            points=offer.eco_points,
            reason=f"Offer accepted from {offer.offer_type}"
        )

        # Optional: update ewaste status
        ewaste.status = 'rewarded'
        ewaste.save()

        return Response({"message": "Offer accepted and ecoPoints awarded."})
