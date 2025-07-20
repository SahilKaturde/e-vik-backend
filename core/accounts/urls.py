from django.urls import path
from .views import (
    RegisterView, MyTokenObtainPairView, UserMeView,
    EwasteCreateView, EwasteListView, UserEwasteListView,
    LeaderboardView, RewardMatchView, RewardListView,
    RewardRedeemView, EcoPointTransactionListView, UserRewardListView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("me/", UserMeView.as_view()),
    path("e-waste/upload/", EwasteCreateView.as_view(), name='upload-ewaste'),
    path('e-waste/list/', EwasteListView.as_view(), name='ewaste-list'),
    path('e-waste/user/', UserEwasteListView, name='user-ewaste'),
    path("leaderboard/", LeaderboardView.as_view(), name="leaderboard"),
    path('rewards/check/', RewardMatchView.as_view(), name='reward-check'),
    path('rewards/all/', RewardListView.as_view(), name='rewards-all'),
    path("rewards/redeem/<int:reward_id>/", RewardRedeemView.as_view(), name="reward-redeem"),
    path("eco/transactions/", EcoPointTransactionListView.as_view(), name="eco-transactions"),
    path('rewards/my/', UserRewardListView.as_view(), name='user-rewards'),
]

from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns += router.urls
