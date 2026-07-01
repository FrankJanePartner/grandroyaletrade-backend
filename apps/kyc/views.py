from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import KYC, ContactMessage
from .serializers import (
    KYCSerializer, SubmitKYCSerializer,
    ContactMessageSerializer, SubmitContactMessageSerializer
)


class SubmitKYCView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = SubmitKYCSerializer(data=request.data)
        if serializer.is_valid():
            kyc, created = KYC.objects.update_or_create(
                user=request.user,
                defaults={
                    'full_name': serializer.validated_data['full_name'],
                    'country': serializer.validated_data['country'],
                    'dob': serializer.validated_data['dob'],
                    'phone': serializer.validated_data['phone'],
                    'id_document_path': serializer.validated_data.get('id_document_path'),
                    'selfie_path': serializer.validated_data.get('selfie_path'),
                }
            )
            return Response(KYCSerializer(kyc).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetKYCView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            kyc = KYC.objects.get(user=request.user)
            return Response(KYCSerializer(kyc).data)
        except KYC.DoesNotExist:
            return Response({'error': 'KYC not found'}, status=status.HTTP_404_NOT_FOUND)


class SubmitContactMessageView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = SubmitContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            message = ContactMessage.objects.create(
                name=serializer.validated_data['name'],
                email=serializer.validated_data['email'],
                subject=serializer.validated_data['subject'],
                message=serializer.validated_data['message'],
            )
            return Response(ContactMessageSerializer(message).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
