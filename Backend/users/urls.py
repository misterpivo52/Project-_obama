from django.urls import path
from users import views


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
    path("favorite/", views.SetFavoriteCryptoView.as_view()),
    path("dashboard/symbol/", views.SetDashboardCryptoView.as_view()),
]
