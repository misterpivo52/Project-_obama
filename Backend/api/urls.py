from django.urls import path
from .views import CurrentPriceView, PriceHistoryView

urlpatterns = [
    path("crypto/<str:symbol>/", CurrentPriceView.as_view()),
    path("crypto/<str:symbol>/history/", PriceHistoryView.as_view()),
]
