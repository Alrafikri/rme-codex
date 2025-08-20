from django.urls import reverse
from rest_framework.test import APITestCase
from apps.tenants.models import Tenant
from apps.users.models import User
from apps.patients.models import Patient
from apps.queue.models import QueueTicket


class CheckInMeasureTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="T", subdomain="t")
        self.user = User.objects.create_user(
            username="staff", password="pass", tenant=self.tenant, role=User.Role.STAFF
        )
        resp = self.client.post(
            reverse("login"),
            {"username": "staff", "password": "pass"},
            HTTP_X_TENANT_ID=str(self.tenant.id),
        )
        self.token = resp.json()["access"]
        self.patient = Patient.objects.create(
            tenant=self.tenant, full_name="John", mrn="001"
        )

    def auth(self):
        return {
            "HTTP_AUTHORIZATION": f"Bearer {self.token}",
            "HTTP_X_TENANT_ID": str(self.tenant.id),
        }

    def test_checkin_creates_queue_ticket(self):
        resp = self.client.post(
            "/api/admissions/checkin/",
            {"patient_id": str(self.patient.id)},
            **self.auth(),
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(QueueTicket.objects.count(), 1)
