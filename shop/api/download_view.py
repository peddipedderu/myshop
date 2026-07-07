from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class DownloadAppView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({
            "download_url": "https://pinkcycle.co.ke/downloads/pinkcycle.apk",
            "version": "1.0.0",
            "platform": "Android"
        })
