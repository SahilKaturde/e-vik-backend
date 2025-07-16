from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from .serializers import RegisterSerializer,RewardSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import EwasteSerializer,UserProfile
from .models import Ewaste,Reward,EcoPoint,EcoPointTransaction
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework.generics import ListAPIView

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [AllowAny]


class EwasteCreateView(generics.CreateAPIView):
    serializer_class = EwasteSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}
    
class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            profile = user.userprofile
            return Response({
                "username": user.username,
                "email": user.email,
                "address": profile.address,
                "profile_pic": request.build_absolute_uri(profile.profile_pic.url) if profile.profile_pic else None
            })
        except:
            return Response({"error": "User profile not found"}, status=404)
        
class EwasteListView(generics.ListAPIView):
    queryset = Ewaste.objects.all().order_by('-id')  # recent first
    serializer_class = EwasteSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        return {'request': self.request}
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def UserEwasteListView(request):
    user = request.user
    user_items = Ewaste.objects.filter(user=user).order_by("-created_at")
    serializer = EwasteSerializer(user_items, many=True, context={"request": request})
    return Response(serializer.data)

class LeaderboardView(APIView):
    permission_classes = [AllowAny]

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
                "profile_pic": request.build_absolute_uri(profile.profile_pic.url) if profile and profile.profile_pic else None
            })

        return Response(leaderboard)
    
# views.py
from .models import UserReward, Reward, EcoPointTransaction
from django.shortcuts import get_object_or_404


    
class RewardListView(ListAPIView):
    queryset = Reward.objects.filter(is_active=True)
    serializer_class = RewardSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class RewardRedeemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reward_id):
        user = request.user
        try:
            reward = Reward.objects.get(id=reward_id, is_active=True)
        except Reward.DoesNotExist:
            return Response({"error": "Reward not found"}, status=404)

        # Calculate available points using transactions only
        transactions = EcoPointTransaction.objects.filter(user=user)
        earned_points = transactions.filter(points__gt=0).aggregate(total=Sum('points'))['total'] or 0
        spent_points = abs(transactions.filter(points__lt=0).aggregate(total=Sum('points'))['total'] or 0)
        available_points = earned_points - spent_points

        # Debug output
        print(f"User: {user.username}")
        print(f"Earned points: {earned_points}")
        print(f"Spent points: {spent_points}")
        print(f"Available points: {available_points}")
        print(f"Reward required: {reward.eco_points_required}")

        if available_points < reward.eco_points_required:
            return Response({"error": "Not enough eco points"}, status=400)

        # Create user reward record
        user_reward = UserReward.objects.create(user=user, reward=reward)

        # Record transaction
        EcoPointTransaction.objects.create(
            user=user,
            points=-reward.eco_points_required,
            reason=f"Redeemed: {reward.name}"
        )

        return Response({
            "message": f"Successfully redeemed {reward.name}",
            "remaining_points": available_points - reward.eco_points_required
        }, status=200)   


class EcoPointTransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = EcoPointTransaction.objects.filter(user=request.user).order_by("-created_at")
        data = []
        for tx in transactions:
            data.append({
                "id": tx.id,
                "points": tx.points,
                "reason": tx.reason,
                "ewaste_title": tx.ewaste.title if tx.ewaste else None,
                "created_at": tx.created_at,
            })
        return Response(data)

# views.py
class UserRewardListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rewards = UserReward.objects.filter(user=request.user).select_related("reward").order_by("-redeemed_at")
        data = [
            {
                "name": r.reward.name,
                "description": r.reward.description,
                "image": request.build_absolute_uri(r.reward.image.url) if r.reward.image else None,
                "redeemed_at": r.redeemed_at,
            }
            for r in rewards
        ]
        return Response(data)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import EcoPoint, Reward
from django.db.models import Sum
from .serializers import RewardSerializer

class RewardMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        total_points = EcoPoint.objects.filter(ewaste__user=user).aggregate(total=Sum('points'))['total'] or 0

        rewards = Reward.objects.filter(eco_points_required=total_points, is_active=True)
        serializer = RewardSerializer(rewards, many=True)

        return Response({
            "user": user.username,
            "total_eco_points": total_points,
            "matched_rewards": serializer.data
        })
