from rest_framework import serializers
from .models import User, UserProfile, UserCryptoAsset
import re

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'country', 'phone']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('User with this email already exists')
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError('Invalid email format')
        return value

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError('User with this phone already exists')
        pattern = r'^\+?[1-9]\d{1,14}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError('Invalid phone format')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            country=validated_data['country'],
            phone=validated_data['phone']
        )
        user.is_active = False
        user.email_verified = False
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'country', 'phone',
            'discord_id', 'two_factor_enabled', 'email_verified',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'discord_id', 'email_verified']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    favorite_crypto_symbol = serializers.CharField(
        source="favorite_crypto.symbol",
        read_only=True,
    )

    class Meta:
        model = UserProfile
        fields = ["favorite_crypto", "favorite_crypto_symbol"]


class UserCryptoAssetSerializer(serializers.ModelSerializer):
    crypto_symbol = serializers.CharField(source="crypto.symbol", read_only=True)
    crypto_name = serializers.CharField(source="crypto.name", read_only=True)

    class Meta:
        model = UserCryptoAsset
        fields = ["id", "crypto", "crypto_symbol", "crypto_name", "amount"]


class UserPortfolioUpdateSerializer(serializers.ModelSerializer):
    crypto = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=20, decimal_places=8)

    class Meta:
        model = UserCryptoAsset
        fields = ["crypto", "amount"]