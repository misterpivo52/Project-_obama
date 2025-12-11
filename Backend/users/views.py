from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.conf import settings
from django.shortcuts import redirect
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
import requests
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from api.models import CryptoAsset
from api.cmc.services import fetch_and_save_full
from users.models import UserProfile, UserCryptoAsset
from users.serializers import (
    UserCryptoAssetSerializer,
    UserPortfolioUpdateSerializer,
    UserProfileSerializer,
)

def get_client_ip(request):
    x = request.META.get('HTTP_X_FORWARDED_FOR')
    if x:
        return x.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def send_email(to, subject, body):
    api = settings.SENDGRID_API_KEY
    sender = settings.DEFAULT_FROM_EMAIL
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {"Authorization": f"Bearer {api}", "Content-Type": "application/json"}
    payload = {
        "personalizations": [{"to": [{"email": to}]}],
        "from": {"email": sender},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}]
    }
    requests.post(url, headers=headers, data=json.dumps(payload))


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        code = user.generate_verification_code()
        link = f"http://localhost:8000/auth/verify-email/?uid={user.id}&code={code}"
        send_email(
            user.email,
            "Verify your email",
            f"Your verification code: {code}\nOr click the link: {link}"
        )
        return Response({"message": "Verify your email to activate account"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def verify_email(request):
    if request.method == "GET":
        user_id = request.GET.get("uid")
        code = request.GET.get("code")
    else:
        user_id = request.data.get("uid")
        code = request.data.get("code")

    if not user_id or not code:
        return Response({"error": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if not user.verify_code(code):
        return Response({"error": "Invalid or expired code"}, status=status.HTTP_400_BAD_REQUEST)

    user.email_verified = True
    user.is_active = True
    user.save()

    return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_email_verification(request):
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    code = user.generate_verification_code()
    link = f"http://localhost:8000/auth/verify-email/?uid={user.id}&code={code}"
    send_email(
        user.email,
        "Verify your email",
        f"Your verification code: {code}\nOr click the link: {link}"
    )

    return Response({"message": "Verification email sent"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    user = authenticate(email=email, password=password)

    if not user:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.email_verified:
        return Response({'error': 'Email not verified'}, status=460)

    if not user.is_active:
        return Response({'error': 'Account disabled'}, status=status.HTTP_403_FORBIDDEN)

    if user.two_factor_enabled:
        code = user.generate_verification_code()
        ip = get_client_ip(request)
        location = 'Unknown'
        if user.discord_id:
            try:
                requests.post(
                    f"{settings.BOT_URL}/send-code",
                    json={'discord_id': user.discord_id, 'code': code, 'email': user.email, 'ip': ip, 'location': location},
                    timeout=5
                )
            except:
                return Response({'error': 'Discord bot offline'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'requires_2fa': True, 'user_id': str(user.id)}, status=status.HTTP_200_OK)

    send_email(
        user.email,
        "New Login Detected",
        f"Hello, {user.first_name}. A new login to your account occurred."
    )

    return Response({'user': UserSerializer(user).data, 'tokens': user.get_tokens()}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_2fa(request):
    user_id = request.data.get('user_id')
    code = request.data.get('code')

    if not user_id or not code:
        return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if not user.verify_code(code):
        return Response({'error': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)

    send_email(
        user.email,
        "New Login Detected (2FA)",
        f"Hello, {user.first_name}. You successfully logged in using 2FA."
    )

    return Response({'user': UserSerializer(user).data, 'tokens': user.get_tokens()}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.invalidate_tokens()
    return Response({'message': 'Logged out'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response(UserSerializer(request.user).data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    r = request.data.get('refresh')
    if not r:
        return Response({'error': 'Refresh token required'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(User.refresh_access_token(r))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unlink_discord(request):
    user = request.user
    user.discord_id = None
    user.two_factor_enabled = False
    user.save()
    return Response({'message': 'Discord unlinked', 'two_factor_enabled': False})


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except:
        return Response({'message': 'If exists, code sent'}, status=status.HTTP_200_OK)

    code = user.generate_verification_code()
    ip = get_client_ip(request)
    location = 'Unknown'

    if user.discord_id:
        try:
            requests.post(
                f"{settings.BOT_URL}/send-password-reset",
                json={'discord_id': user.discord_id, 'code': code, 'email': email, 'ip': ip, 'location': location},
                timeout=5
            )
            return Response({'message': 'Reset code sent via Discord'}, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Discord bot error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    send_email(
        user.email,
        "Password Reset Code",
        f"Your reset code is: {code}"
    )

    return Response({'message': 'Reset code sent via email'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request):
    email = request.data.get('email')
    code = request.data.get('code')
    new_password = request.data.get('new_password')

    if not email or not code or not new_password:
        return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except:
        return Response({'error': 'Invalid email or code'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.verify_code(code):
        return Response({'error': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)

    if len(new_password) < 8:
        return Response({'error': 'Password too short'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    send_email(
        user.email,
        "Password Reset Successful",
        "Your password has been changed successfully."
    )

    return Response({'message': 'Password reset successful'})
  
class UserPortfolioView(APIView):
    def get(self, request):
        user = request.user
        portfolio = UserCryptoAsset.objects.filter(user=user)
        ser = UserCryptoAssetSerializer(portfolio, many=True)
        return Response(ser.data)


class AddCryptoToPortfolioView(APIView):
    def post(self, request):
        user = request.user
        crypto_id = request.data.get("crypto")
        amount = float(request.data.get("amount", 0))

        try:
            crypto = CryptoAsset.objects.get(id=crypto_id)
        except CryptoAsset.DoesNotExist:
            return Response({"error": "Crypto not found"}, status=404)

        record, _ = UserCryptoAsset.objects.get_or_create(
            user=user,
            crypto=crypto,
            defaults={"amount": 0},
        )

        record.amount += amount
        record.save()

        return Response({"status": "added", "amount": record.amount})


class RemoveCryptoFromPortfolioView(APIView):
    def post(self, request):
        user = request.user
        crypto_id = request.data.get("crypto")
        amount = float(request.data.get("amount", 0))

        try:
            record = UserCryptoAsset.objects.get(user=user, crypto_id=crypto_id)
        except UserCryptoAsset.DoesNotExist:
            return Response({"error": "Record not found"}, status=404)

        record.amount -= amount
        if record.amount < 0:
            record.amount = 0
        record.save()

        return Response({"status": "removed", "amount": record.amount})


class SetFavoriteCryptoView(APIView):
    def post(self, request):
        user = request.user
        crypto_id = request.data.get("crypto")

        try:
            crypto = CryptoAsset.objects.get(id=crypto_id)
        except CryptoAsset.DoesNotExist:
            return Response({"error": "Crypto not found"}, status=404)

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.favorite_crypto = crypto
        profile.save()

        return Response({"favorite": crypto.symbol})


class SetDashboardCryptoView(APIView):
    def post(self, request):
        user = request.user
        symbol = str(request.data.get("symbol", "")).upper().strip()
        if not symbol:
            return Response({"error": "Symbol is required"}, status=400)

        crypto, _ = CryptoAsset.objects.get_or_create(
            symbol=symbol,
            defaults={"name": symbol},
        )
        try:
            fetch_and_save_full(symbol)
        except Exception as exc:
            return Response({"error": f"Failed to fetch data for {symbol}: {exc}"}, status=400)

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.favorite_crypto = crypto
        profile.save()

        return Response(
            {
                "symbol": symbol,
                "message": f"{symbol} pinned to dashboard",
            }
        )

