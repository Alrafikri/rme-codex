from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import QueueTicket
from .serializers import QueueTicketSerializer
from apps.tenants.permissions import IsTenantUser, RolePermission
from apps.users.models import User


class QueueTicketViewSet(viewsets.ViewSet):
    serializer_class = QueueTicketSerializer
    permission_classes = [IsAuthenticated, IsTenantUser, RolePermission]
    required_roles = [
        User.Role.ADMIN,
        User.Role.DOCTOR,
        User.Role.NURSE,
        User.Role.STAFF,
    ]

    def list(self, request):
        qs = QueueTicket.objects.filter(tenant=request.tenant).exclude(
            state=QueueTicket.State.DONE
        ).order_by("created_at")
        return Response(QueueTicketSerializer(qs, many=True).data)

    @action(detail=False, methods=["post"])
    def next(self, request):
        with transaction.atomic():
            ticket = (
                QueueTicket.objects.select_for_update()
                .filter(tenant=request.tenant, state=QueueTicket.State.WAITING)
                .order_by("created_at")
                .first()
            )
            if not ticket:
                return Response({"detail": "empty"}, status=status.HTTP_404_NOT_FOUND)
            ticket.state = QueueTicket.State.IN_PROGRESS
            ticket.save()
            return Response(QueueTicketSerializer(ticket).data)

    @action(detail=True, methods=["post"])
    def done(self, request, pk=None):
        ticket = QueueTicket.objects.get(pk=pk, tenant=request.tenant)
        ticket.state = QueueTicket.State.DONE
        ticket.save()
        return Response(QueueTicketSerializer(ticket).data)

    @action(detail=True, methods=["post"])
    def skip(self, request, pk=None):
        ticket = QueueTicket.objects.get(pk=pk, tenant=request.tenant)
        ticket.state = QueueTicket.State.SKIPPED
        ticket.save()
        return Response(QueueTicketSerializer(ticket).data)
