from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from api.ai.analysis import (
    analyze_symbol,
    analyze_portfolio,
    analyze_symbol_openai,
    analyze_portfolio_openai,
)
from api.ai.gemini_client import GeminiError
from api.ai.openai_client import OpenAIError


class GeminiAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        symbol = request.data.get("symbol", "")
        lang = request.data.get("lang", "uk")
        try:
            result = analyze_symbol(symbol, lang=lang)
            return Response(result)
        except (ValueError, GeminiError) as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class GeminiPortfolioAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        lang = request.query_params.get("lang", "uk")
        try:
            result = analyze_portfolio(request.user, lang=lang)
            return Response(result)
        except (ValueError, GeminiError) as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class OpenAIAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        symbol = request.data.get("symbol", "")
        lang = request.data.get("lang", "uk")
        try:
            result = analyze_symbol_openai(symbol, lang=lang)
            return Response(result)
        except (ValueError, OpenAIError) as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class OpenAIPortfolioAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        lang = request.query_params.get("lang", "uk")
        try:
            result = analyze_portfolio_openai(request.user, lang=lang)
            return Response(result)
        except (ValueError, OpenAIError) as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
