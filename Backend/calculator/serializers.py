from rest_framework import serializers
from .models import CryptoConversion

class CryptoConvertSerializer(serializers.Serializer):
    """Serializer for conversion request"""
    from_currency = serializers.CharField(max_length=20)
    to_currency = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=20, decimal_places=8, min_value=0)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value

class CryptoConversionSerializer(serializers.ModelSerializer):
    """Serializer for conversion history"""
    class Meta:
        model = CryptoConversion
        fields = ['id', 'from_currency', 'to_currency', 'amount', 'result', 'rate', 'created_at']
        read_only_fields = ['id', 'created_at']