import uuid
from django.db import models
from django.utils import timezone
from apps.tenants.models import Tenant


class QueueTicket(models.Model):
    class State(models.TextChoices):
        WAITING = "WAITING", "WAITING"
        IN_PROGRESS = "IN_PROGRESS", "IN_PROGRESS"
        DONE = "DONE", "DONE"
        SKIPPED = "SKIPPED", "SKIPPED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    visit = models.ForeignKey(
        "admissions.Visit", on_delete=models.CASCADE, related_name="queue_ticket"
    )
    number = models.PositiveIntegerField()
    state = models.CharField(
        max_length=20, choices=State.choices, default=State.WAITING
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "number"], name="uniq_queue_number_per_tenant"
            )
        ]
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.number} - {self.state}"
