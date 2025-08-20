from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema


class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()


class HealthzView(APIView):
    permission_classes = [AllowAny]
    serializer_class = HealthSerializer

    @extend_schema(responses=HealthSerializer)
    def get(self, request):
        return Response({"status": "ok"})
