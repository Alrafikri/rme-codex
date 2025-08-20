from django.core.management.base import BaseCommand
from apps.tenants.models import Tenant
from apps.users.models import User


class Command(BaseCommand):
    help = "Seed superadmin and demo clinic admin"

    def handle(self, *args, **options):
        system, _ = Tenant.objects.get_or_create(
            subdomain="system", defaults={"name": "System"}
        )
        clinic, _ = Tenant.objects.get_or_create(
            subdomain="clinic", defaults={"name": "Demo Clinic"}
        )
        if not User.objects.filter(username="superadmin").exists():
            User.objects.create_user(
                username="superadmin",
                password="password",
                tenant=system,
                role=User.Role.SUPERADMIN,
            )
        if not User.objects.filter(username="clinicadmin").exists():
            User.objects.create_user(
                username="clinicadmin",
                password="password",
                tenant=clinic,
                role=User.Role.ADMIN,
            )
        self.stdout.write(self.style.SUCCESS("Seeded demo tenants and users"))
