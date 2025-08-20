from django.urls import reverse
from rest_framework.test import APITestCase
from apps.tenants.models import Tenant
from apps.users.models import User
from apps.patients.models import Patient


class QueueAcceptanceTests(APITestCase):
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
        self.p1 = Patient.objects.create(tenant=self.tenant, full_name="A", mrn="1")
        self.p2 = Patient.objects.create(tenant=self.tenant, full_name="B", mrn="2")
        self.auth_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.token}",
            "HTTP_X_TENANT_ID": str(self.tenant.id),
        }
        for p in (self.p1, self.p2):
            self.client.post(
                "/api/admissions/checkin/",
                {"patient_id": str(p.id)},
                **self.auth_headers,
            )

    def test_call_next_done_flow(self):
        resp1 = self.client.post("/api/queue/next/", **self.auth_headers)
        first_id = resp1.json()["id"]
        self.client.post(f"/api/queue/{first_id}/done/", **self.auth_headers)
        resp2 = self.client.post("/api/queue/next/", **self.auth_headers)
        self.assertEqual(resp2.json()["patient_name"], "B")
