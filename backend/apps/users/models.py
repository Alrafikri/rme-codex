import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.tenants.models import Tenant


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERADMIN = "SUPERADMIN", "Super Admin"
        ADMIN = "ADMIN", "Clinic Admin"
        DOCTOR = "DOCTOR", "Doctor"
        NURSE = "NURSE", "Nurse"
        STAFF = "STAFF", "Staff"
        CASHIER = "CASHIER", "Cashier"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Role.choices)
