# urls.py
from django.urls import path
from .views import UserOffersView, AcceptOfferView, RejectOfferView, SendOfferView

urlpatterns = [
    path('offers/', UserOffersView.as_view(), name='user-offers'),
    path('offers/<int:offer_id>/accept/', AcceptOfferView.as_view(), name='accept-offer'),
    path('offers/<int:offer_id>/reject/', RejectOfferView.as_view(), name='reject-offer'),
    path('send-offer/', SendOfferView.as_view(), name='send-offer'),
]