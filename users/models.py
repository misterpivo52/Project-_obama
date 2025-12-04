from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
import random

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    country = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, unique=True)
    discord_id = models.CharField(max_length=50, null=True, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    code_expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_tokens(self):
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}

    def invalidate_tokens(self):
        pass

    def generate_verification_code(self):
        code = str(random.randint(100000, 999999))
        self.verification_code = code
        self.code_expires_at = timezone.now() + timezone.timedelta(minutes=5)
        self.save(update_fields=["verification_code", "code_expires_at"])
        return code

    def verify_code(self, code):
        if self.verification_code != code:
            return False
        if not self.code_expires_at or timezone.now() > self.code_expires_at:
            return False
        self.verification_code = None
        self.code_expires_at = None
        self.save(update_fields=["verification_code", "code_expires_at"])
        return True

    def set_random_password(self):
        new_pass = BaseUserManager().make_random_password()
        self.set_password(new_pass)
        self.save()
        return new_pass
