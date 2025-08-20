from django.urls import reverse
from rest_framework.test import APITestCase
from apps.tenants.models import Tenant
from apps.users.models import User


class AuthTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Clinic", subdomain="clinic")
        User.objects.create_user(
            username="admin",
            password="password",
            tenant=self.tenant,
            role=User.Role.ADMIN,
        )

    def test_login_returns_token(self):
        url = reverse("login")
        response = self.client.post(
            url,
            {"username": "admin", "password": "password"},
            HTTP_X_TENANT_ID=str(self.tenant.id),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
