from django.http import HttpResponseBadRequest
from .models import Tenant


class TenantMiddleware:
    """Resolve tenant from subdomain or X-Tenant-ID header."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/api/healthz"):
            return self.get_response(request)

        tenant_id = request.META.get("HTTP_X_TENANT_ID")
        tenant = None
        if tenant_id:
            try:
                tenant = Tenant.objects.get(id=tenant_id)
            except Tenant.DoesNotExist:
                return HttpResponseBadRequest("Invalid tenant")
        else:
            host = request.get_host().split(":")[0]
            subdomain = host.split(".")[0]
            try:
                tenant = Tenant.objects.get(subdomain=subdomain)
            except Tenant.DoesNotExist:
                return HttpResponseBadRequest("Invalid tenant")
        request.tenant = tenant
        return self.get_response(request)
