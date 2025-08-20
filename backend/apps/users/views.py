from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer
from apps.tenants.permissions import IsTenantUser, RolePermission


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsTenantUser, RolePermission]
    required_roles = [User.Role.ADMIN, User.Role.SUPERADMIN]
    queryset = User.objects.all()
    lookup_field = "id"

    def get_queryset(self):
        return User.objects.filter(tenant=self.request.tenant)
