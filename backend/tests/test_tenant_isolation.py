from django.urls import reverse
from rest_framework.test import APITestCase
from apps.tenants.models import Tenant
from apps.users.models import User


class TenantIsolationTests(APITestCase):
    def setUp(self):
        self.t1 = Tenant.objects.create(name="T1", subdomain="t1")
        self.t2 = Tenant.objects.create(name="T2", subdomain="t2")
        User.objects.create_user(
            username="u1", password="pass", tenant=self.t1, role=User.Role.ADMIN
        )
        User.objects.create_user(
            username="u2", password="pass", tenant=self.t2, role=User.Role.ADMIN
        )
        resp = self.client.post(
            reverse("login"),
            {"username": "u1", "password": "pass"},
            HTTP_X_TENANT_ID=str(self.t1.id),
        )
        self.token = resp.json()["access"]

    def test_cross_tenant_blocked(self):
        ok = self.client.get(
            "/api/users/",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
            HTTP_X_TENANT_ID=str(self.t1.id),
        )
        self.assertEqual(ok.status_code, 200)
        other = self.client.get(
            "/api/users/",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
            HTTP_X_TENANT_ID=str(self.t2.id),
        )
        self.assertEqual(other.status_code, 403)
