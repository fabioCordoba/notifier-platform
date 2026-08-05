from rest_framework.permissions import BasePermission

from apps.authentication.models.role import HierarchyLevel


# ──────────────────────────────────────────────
# Clases legacy (mantienen compatibilidad)
# ──────────────────────────────────────────────

class IsSuperOrReadOnly(BasePermission):
    """Legacy: is_staff → escritura; cualquier autenticado → lectura."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsAdminOrReadOnly(BasePermission):
    """Legacy: role code_name='admin' → escritura."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.roles.filter(code_name='admin').exists()
        )


# ──────────────────────────────────────────────
# Jerarquía de acceso
# ──────────────────────────────────────────────

class IsPlatformAdmin(BasePermission):
    """
    Superusuario de plataforma (is_staff=True).
    Acceso total: puede gestionar cualquier organización y usuario.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )


class IsOrgAdmin(BasePermission):
    """
    Administrador cliente (hierarchy_level=org_admin).
    Control total dentro de su propia organización.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.roles.filter(hierarchy_level=HierarchyLevel.ORG_ADMIN).exists()
        )


class IsOrgAdminOrAbove(BasePermission):
    """
    Platform admin O org_admin.
    Puede crear y gestionar usuarios subordinados.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_staff:
            return True
        return request.user.roles.filter(
            hierarchy_level__in=[HierarchyLevel.PLATFORM_ADMIN, HierarchyLevel.ORG_ADMIN]
        ).exists()


class IsSupervisorOrAbove(BasePermission):
    """
    Supervisor, org_admin o platform_admin.
    Puede consultar usuarios en su organización.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_staff:
            return True
        return request.user.roles.filter(
            hierarchy_level__in=[
                HierarchyLevel.PLATFORM_ADMIN,
                HierarchyLevel.ORG_ADMIN,
                HierarchyLevel.SUPERVISOR,
            ]
        ).exists()
