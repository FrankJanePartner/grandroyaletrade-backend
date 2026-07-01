from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, UserRole
import bcrypt


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    role = serializers.CharField(source='user.role_profile.role', read_only=True)
    
    class Meta:
        model = Profile
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'referral_code', 'referred_by', 'role', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'profile']


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    referral_code = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value
    
    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        phone = validated_data.get('phone', '')
        referral_code_input = validated_data.get('referral_code', '')
        
        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save()
        
        # Create user role
        UserRole.objects.create(user=user, role='user')
        
        # Create profile
        referral_code = Profile.generate_referral_code(first_name)
        referred_by = None
        
        if referral_code_input:
            try:
                referred_by = Profile.objects.get(referral_code__iexact=referral_code_input).user
            except Profile.DoesNotExist:
                pass
        
        profile = Profile.objects.create(
            user=user,
            phone=phone,
            referral_code=referral_code,
            referred_by=referred_by.profile if referred_by else None
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(min_length=6, write_only=True)


class UpdateProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    password = serializers.CharField(min_length=6, required=False, write_only=True)
    
    def update(self, instance, validated_data):
        if 'first_name' in validated_data:
            instance.first_name = validated_data['first_name']
        if 'last_name' in validated_data:
            instance.last_name = validated_data['last_name']
        if 'phone' in validated_data:
            instance.profile.phone = validated_data['phone']
            instance.profile.save()
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance
