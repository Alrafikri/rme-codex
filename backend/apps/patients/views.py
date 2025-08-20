from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import Patient
from .serializers import PatientSerializer
from apps.tenants.permissions import IsTenantUser, RolePermission
from apps.users.models import User


class PatientPagination(PageNumberPagination):
    page_size = 10


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsTenantUser, RolePermission]
    required_roles = [
        User.Role.ADMIN,
        User.Role.DOCTOR,
        User.Role.NURSE,
        User.Role.STAFF,
    ]
    queryset = Patient.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["full_name", "mrn", "nik", "bpjs"]
    pagination_class = PatientPagination
    lookup_field = "id"

    def get_queryset(self):
        return Patient.objects.filter(tenant=self.request.tenant).order_by("full_name")

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)
