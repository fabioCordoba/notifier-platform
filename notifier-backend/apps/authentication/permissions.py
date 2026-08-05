from rest_framework.permissions import BasePermission
from apps.organizations.models import ApiKey


class IsApiKeyAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.auth, ApiKey) and request.auth.is_active
