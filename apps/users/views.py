from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from .models import Profile, UserRole
from .serializers import (
    RegisterSerializer, LoginSerializer, ProfileSerializer,
    UpdateProfileSerializer, UserSerializer
)
from .auth import generate_jwt_token


class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = generate_jwt_token(user)
            return Response({
                'token': token,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    token = generate_jwt_token(user)
                    return Response({
                        'token': token,
                        'user': UserSerializer(user).data
                    })
                else:
                    return Response(
                        {'error': 'Invalid email or password'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
            except User.DoesNotExist:
                return Response(
                    {'error': 'Invalid email or password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        profile = request.user.profile
        role = request.user.role_profile.role
        
        return Response({
            'id': str(request.user.id),
            'email': request.user.email,
            'firstName': request.user.first_name,
            'lastName': request.user.last_name,
            'phone': profile.phone,
            'referralCode': profile.referral_code,
            'referredBy': profile.referred_by.referral_code if profile.referred_by else None,
            'role': role,
            'isVerified': True,
            'createdAt': request.user.date_joined.isoformat(),
        })


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({'ok': True})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyPasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        password = request.data.get('password')
        if not password:
            return Response({'ok': False})
        
        if request.user.check_password(password):
            return Response({'ok': True})
        return Response({'ok': False})
