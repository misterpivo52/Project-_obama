from django.urls import path
from . import views

app_name = 'calculator'

urlpatterns = [
    path('convert/', views.convert_crypto, name='convert'),
    path('history/', views.conversion_history, name='history'),
    path('price/', views.get_crypto_price, name='price'),
]