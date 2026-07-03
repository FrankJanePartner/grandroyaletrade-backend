from rest_framework import serializers
from .models import User
from django.db import transaction
from rest_framework import serializers
from .models import User
from .validators import validate_password_strength
from .utils import generate_referral_code
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "referral_code",
            "is_verified",
            "date_joined",
        )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )
    confirm_password = serializers.CharField(
        write_only=True
    )
    referral_code = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True
    )
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password",
            "referral_code",
        )
            def validate(self, attrs):

        if attrs["password"] != attrs["confirm_password"]:

            raise serializers.ValidationError(
                {
                    "confirm_password":
                    "Passwords do not match."
                }
            )

        validate_password_strength(attrs["password"])

        return attrs
        @transaction.atomic
    def create(self, validated_data):

        referral = validated_data.pop(
            "referral_code",
            None
        )

        validated_data.pop("confirm_password")

        referred_by = None

        if referral:

            try:
                referred_by = User.objects.get(
                    referral_code=referral
                )

            except User.DoesNotExist:

                raise serializers.ValidationError(
                    {
                        "referral_code":
                        "Invalid referral code."
                    }
                )

        user = User.objects.create_user(

            email=validated_data["email"],

            password=validated_data["password"],

            first_name=validated_data["first_name"],

            last_name=validated_data["last_name"],

            referred_by=referred_by,
        )

        while True:

            code = generate_referral_code()

            if not User.objects.filter(
                referral_code=code
            ).exists():

                user.referral_code = code

                break

        user.save()

        return user
    
    
class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField()

    remember_me = serializers.BooleanField(
        default=False
    )

    def validate(self, attrs):

        email = attrs.get("email")

        password = attrs.get("password")

        user = authenticate(
            username=email,
            password=password,
        )

        if not user:

            raise serializers.ValidationError(
                "Invalid email or password."
            )

        if not user.is_active:

            raise serializers.ValidationError(
                "Account is disabled."
            )

        attrs["user"] = user

        return attrs

    def get_tokens(self, user):

        refresh = RefreshToken.for_user(user)

        return {

            "refresh": str(refresh),

            "access": str(refresh.access_token),
        }