from django.urls import path
from .views import CurrentPriceView, PriceHistoryView, CalculatorView
from .ai_views import (
    GeminiAnalysisView,
    GeminiPortfolioAnalysisView,
    OpenAIAnalysisView,
    OpenAIPortfolioAnalysisView,
)

urlpatterns = [
    path("crypto/<str:symbol>/", CurrentPriceView.as_view()),
    path("crypto/<str:symbol>/history/", PriceHistoryView.as_view()),
    path("calculator/", CalculatorView.as_view()),
    path("ai/analysis/", GeminiAnalysisView.as_view()),
    path("ai/portfolio/", GeminiPortfolioAnalysisView.as_view()),
    path("openai/analysis/", OpenAIAnalysisView.as_view()),
    path("openai/portfolio/", OpenAIPortfolioAnalysisView.as_view()),
]
