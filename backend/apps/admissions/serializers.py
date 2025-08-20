from rest_framework import serializers
from apps.queue.models import QueueTicket
from apps.queue.serializers import QueueTicketSerializer


class CheckInSerializer(serializers.Serializer):
    patient_id = serializers.UUIDField()


class CheckInResponseSerializer(QueueTicketSerializer):
    class Meta(QueueTicketSerializer.Meta):
        model = QueueTicket
