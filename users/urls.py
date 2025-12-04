from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('verify-2fa/', views.verify_2fa),
    path('logout/', views.logout),
    path('profile/', views.profile),
    path('profile/update/', views.update_profile),
    path('refresh/', views.refresh_token),
    path('unlink-discord/', views.unlink_discord),
    path('request-password-reset/', views.request_password_reset),
    path('confirm-password-reset/', views.confirm_password_reset),
]
