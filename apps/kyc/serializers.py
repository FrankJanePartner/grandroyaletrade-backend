from rest_framework import serializers
from .models import KYC, ContactMessage


class KYCSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source='user.id', read_only=True)
    
    class Meta:
        model = KYC
        fields = ['id', 'user_id', 'full_name', 'country', 'dob', 'phone', 'id_document_path', 'selfie_path', 'status', 'created_at']


class SubmitKYCSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=200)
    country = serializers.CharField(max_length=100)
    dob = serializers.DateField()
    phone = serializers.CharField(max_length=20)
    id_document_path = serializers.FileField(required=False)
    selfie_path = serializers.FileField(required=False)


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'status', 'created_at']


class SubmitContactMessageSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField()
