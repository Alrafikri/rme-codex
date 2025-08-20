from rest_framework import serializers
from .models import QueueTicket


class QueueTicketSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(
        source="visit.patient.full_name", read_only=True
    )

    class Meta:
        model = QueueTicket
        fields = ["id", "number", "state", "patient_name"]
        read_only_fields = fields
