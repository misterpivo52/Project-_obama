from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid
import secrets

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True)
    discord_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    two_factor_enabled = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    code_expires_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def generate_verification_code(self):
        self.verification_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        from django.utils import timezone
        from datetime import timedelta
        self.code_expires_at = timezone.now() + timedelta(minutes=5)
        self.save()
        return self.verification_code

    def verify_code(self, code):
        from django.utils import timezone
        if not self.verification_code or not self.code_expires_at:
            return False
        if timezone.now() > self.code_expires_at:
            return False
        if self.verification_code == code:
            self.verification_code = None
            self.code_expires_at = None
            self.save()
            return True
        return False