from django.urls import reverse
from rest_framework.test import APITestCase
from apps.tenants.models import Tenant
from apps.users.models import User
from apps.patients.models import Patient


class PatientAPITests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="T1", subdomain="t1")
        self.other = Tenant.objects.create(name="T2", subdomain="t2")
        self.user = User.objects.create_user(
            username="admin",
            password="pass",
            tenant=self.tenant,
            role=User.Role.ADMIN,
        )
        resp = self.client.post(
            reverse("login"),
            {"username": "admin", "password": "pass"},
            HTTP_X_TENANT_ID=str(self.tenant.id),
        )
        self.token = resp.json()["access"]

    def auth(self, tenant_id=None):
        return {
            "HTTP_AUTHORIZATION": f"Bearer {self.token}",
            "HTTP_X_TENANT_ID": str(tenant_id or self.tenant.id),
        }

    def test_crud_patient(self):
        url = "/api/patients/"
        data = {
            "full_name": "John Doe",
            "mrn": "001",
            "nik": "123",
            "bpjs": "456",
        }
        # create
        resp = self.client.post(url, data, **self.auth())
        self.assertEqual(resp.status_code, 201)
        pid = resp.json()["id"]
        # list
        resp = self.client.get(url, **self.auth())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)
        # retrieve
        resp = self.client.get(f"{url}{pid}/", **self.auth())
        self.assertEqual(resp.status_code, 200)
        # update
        resp = self.client.patch(f"{url}{pid}/", {"full_name": "Jane"}, **self.auth())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["full_name"], "Jane")
        # delete
        resp = self.client.delete(f"{url}{pid}/", **self.auth())
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(Patient.objects.count(), 0)

    def test_search_and_pagination(self):
        for i in range(15):
            Patient.objects.create(
                tenant=self.tenant,
                full_name=f"P{i}",
                mrn=f"{i}",
            )
        resp = self.client.get("/api/patients/?page=2", **self.auth())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 15)
        resp = self.client.get("/api/patients/?search=P1", **self.auth())
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["count"] >= 1)

    def test_cross_tenant_access_blocked(self):
        Patient.objects.create(tenant=self.other, full_name="Other", mrn="999")
        resp = self.client.get("/api/patients/", **self.auth(self.other.id))
        self.assertEqual(resp.status_code, 403)
