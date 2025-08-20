from rest_framework.permissions import BasePermission


class IsTenantUser(BasePermission):
    """Ensure the authenticated user belongs to the request tenant."""

    def has_permission(self, request, view):
        user = request.user
        tenant = getattr(request, "tenant", None)
        return bool(
            user and user.is_authenticated and tenant and user.tenant_id == tenant.id
        )


class RolePermission(BasePermission):
    """Ensure user has one of the required roles defined on the view."""

    def has_permission(self, request, view):
        required = getattr(view, "required_roles", [])
        if not required:
            return True
        return getattr(request.user, "role", None) in required
