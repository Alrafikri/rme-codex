import uuid
from django.db import models
from apps.tenants.models import Tenant


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    mrn = models.CharField(max_length=50)
    nik = models.CharField(max_length=20, blank=True)
    bpjs = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "mrn"], name="uniq_patient_mrn_per_tenant"
            ),
        ]

    def __str__(self) -> str:
        return self.full_name
