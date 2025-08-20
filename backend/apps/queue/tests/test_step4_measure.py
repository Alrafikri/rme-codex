from django.urls import reverse
from rest_framework.test import APITestCase
from apps.tenants.models import Tenant
from apps.users.models import User
from apps.patients.models import Patient


class QueueMeasureTests(APITestCase):
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
        # check-in both patients
        for p in (self.p1, self.p2):
            self.client.post(
                "/api/admissions/checkin/",
                {"patient_id": str(p.id)},
                **self.auth_headers,
            )

    def test_next_marks_first_in_progress(self):
        resp = self.client.post("/api/queue/next/", **self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["state"], "IN_PROGRESS")
        # second ticket should remain waiting
        resp = self.client.get("/api/queue/", **self.auth_headers)
        states = [t["state"] for t in resp.json()]
        self.assertEqual(states, ["IN_PROGRESS", "WAITING"])
