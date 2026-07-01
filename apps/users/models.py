from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
import uuid
import random
import string


class UserRole(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role_profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'User Roles'
    
    def __str__(self):
        return f"{self.user.email} - {self.role}"


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    referral_code = models.CharField(max_length=20, unique=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.referral_code}"
    
    @staticmethod
    def generate_referral_code(first_name=''):
        """Generate unique referral code based on first name and random string"""
        prefix = ''.join(c for c in first_name[:3].upper() if c.isalpha()) or 'GRT'
        # Ensure it's at least 3 chars
        while len(prefix) < 3:
            prefix += random.choice(string.ascii_uppercase)
        
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        code = prefix + suffix
        
        # Ensure uniqueness
        while Profile.objects.filter(referral_code=code).exists():
            suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            code = prefix + suffix
        
        return code
