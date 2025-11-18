from django.urls import path
from .views import (
    UserPortfolioView,
    AddCryptoToPortfolioView,
    RemoveCryptoFromPortfolioView,
    SetFavoriteCryptoView,
)

urlpatterns = [
    path("portfolio/", UserPortfolioView.as_view()),
    path("portfolio/add/", AddCryptoToPortfolioView.as_view()),
    path("portfolio/remove/", RemoveCryptoFromPortfolioView.as_view()),
    path("favorite/", SetFavoriteCryptoView.as_view()),
]
