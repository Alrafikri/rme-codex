from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers


class TenantTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        request = self.context["request"]
        if self.user.tenant_id != getattr(request, "tenant", None).id:
            raise serializers.ValidationError("Invalid tenant")
        data["user"] = {"username": self.user.username, "role": self.user.role}
        return data


class TenantTokenObtainPairView(TokenObtainPairView):
    serializer_class = TenantTokenObtainPairSerializer
