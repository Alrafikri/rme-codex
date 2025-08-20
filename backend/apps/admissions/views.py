from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.tenants.permissions import IsTenantUser, RolePermission
from apps.users.models import User
from apps.patients.models import Patient
from apps.queue.models import QueueTicket
from apps.queue.serializers import QueueTicketSerializer
from .models import Visit
from .serializers import CheckInSerializer


class CheckInView(APIView):
    serializer_class = CheckInSerializer
    permission_classes = [IsAuthenticated, IsTenantUser, RolePermission]
    required_roles = [
        User.Role.ADMIN,
        User.Role.DOCTOR,
        User.Role.NURSE,
        User.Role.STAFF,
    ]

    def post(self, request):
        serializer = CheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = Patient.objects.get(
            id=serializer.validated_data["patient_id"], tenant=request.tenant
        )
        visit = Visit.objects.create(tenant=request.tenant, patient=patient)
        number = QueueTicket.objects.filter(tenant=request.tenant).count() + 1
        ticket = QueueTicket.objects.create(
            tenant=request.tenant, visit=visit, number=number
        )
        return Response(
            QueueTicketSerializer(ticket).data, status=status.HTTP_201_CREATED
        )
