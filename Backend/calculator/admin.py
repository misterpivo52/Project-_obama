from django.contrib import admin
from django.contrib import admin
from .models import CryptoConversion

@admin.register(CryptoConversion)
class CryptoConversionAdmin(admin.ModelAdmin):
    list_display = ['user', 'from_currency', 'to_currency', 'amount', 'result', 'created_at']
    list_filter = ['created_at', 'from_currency', 'to_currency']
    search_fields = ['user__username', 'from_currency', 'to_currency']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(user=request.user)
        return queryset
