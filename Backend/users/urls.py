from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('verify-email/', views.verify_email),
    path('send-email-verification/', views.send_email_verification),
    path('verify-2fa/', views.verify_2fa),
    path('logout/', views.logout),
    path('profile/', views.profile),
    path('profile/update/', views.update_profile),
    path('refresh/', views.refresh_token),
    path('unlink-discord/', views.unlink_discord),
    path('request-password-reset/', views.request_password_reset),
    path('confirm-password-reset/', views.confirm_password_reset),
    path("portfolio/", views.UserPortfolioView.as_view()),
    path("portfolio/add/", views.AddCryptoToPortfolioView.as_view()),
    path("portfolio/remove/", views.RemoveCryptoFromPortfolioView.as_view()),
    path("portfolio/swap/preview/", views.SwapPreviewView.as_view()),
    path("portfolio/swap/", views.SwapPortfolioView.as_view()),
    path("favorite/", views.SetFavoriteCryptoView.as_view()),
    path("dashboard/symbol/", views.SetDashboardCryptoView.as_view()),
    path("2fa/google/enable/", views.enable_totp_and_generate_qr_code),
    path("2fa/google/verify/", views.verify_totp_and_enable),
    path("2fa/google/disable/", views.disable_totp),
]
