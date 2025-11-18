from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .serializers import CryptoConvertSerializer, CryptoConversionSerializer
from .services import CalculatorService 
from .models import CryptoConversion

@api_view(['POST'])
@permission_classes([AllowAny])
def convert_crypto(request):
    """
    Cryptocurrency conversion
    POST /api/calculator/convert/
    {
        "from_currency": "bitcoin",
        "to_currency": "ethereum",
        "amount": 1.5
    }
    """
    serializer = CryptoConvertSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    from_crypto = serializer.validated_data['from_currency'].lower()
    to_crypto = serializer.validated_data['to_currency'].lower()
    amount = serializer.validated_data['amount']
    
    result, rate = CalculatorService.convert_crypto(from_crypto, to_crypto, amount)
    
    if result is None:
        return Response(
            {'error': 'Unable to fetch cryptocurrency data'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    if request.user.is_authenticated:
        CryptoConversion.objects.create(
            user=request.user,
            from_currency=from_crypto,
            to_currency=to_crypto,
            amount=amount,
            result=result,
            rate=rate
        )
    
    return Response({
        'from_currency': from_crypto,
        'to_currency': to_crypto,
        'from_amount': float(amount),
        'to_amount': result,
        'rate': rate
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversion_history(request):
    """
    Retrieving user conversion history
    GET /api/calculator/history/
    """
    history = CryptoConversion.objects.filter(user=request.user)
    serializer = CryptoConversionSerializer(history, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_crypto_price(request):
    """
    Getting the current cryptocurrency price
    GET /api/calculator/price/?id=bitcoin&vs_currency=usd
    """
    crypto_id = request.query_params.get('id', 'bitcoin').lower()
    vs_currency = request.query_params.get('vs_currency', 'usd').lower()
    
    price = CalculatorService.get_crypto_price(crypto_id, vs_currency)
    
    if price is None:
        return Response(
            {'error': 'Unable to fetch price'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response({
        'crypto': crypto_id,
        'currency': vs_currency,
        'price': price
    })

