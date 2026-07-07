from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from finance.services.roi import process_all_investments


class ProcessROIAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request):

        secret = request.headers.get("X-CRON-SECRET")

        if secret != settings.CRON_SECRET:

            return Response(
                {
                    "detail": "Unauthorized"
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        processed = process_all_investments()

        return Response(
            {
                "processed": processed
            }
        )