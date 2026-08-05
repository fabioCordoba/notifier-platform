import logging

from django.contrib import admin
from django.utils.html import format_html


def is_super_admin(request):
    """
    return True is user is SuperAdmin
    """
    user = request.user
    return user.is_superuser


def is_staff_admin(request):
    """
    return True is user is Staff (Admin)
    """
    user = request.user
    return user.is_staff


class ModelOnlyShowSuperAdmin(admin.ModelAdmin):
    """
    Only super-admin can see, edit, create and edit the model
    """

    def has_module_permission(self, request, obj=None):
        return is_super_admin(request)

    def has_change_permission(self, request, obj=None):
        return is_super_admin(request)

    def has_view_permission(self, request, obj=None):
        return is_super_admin(request)

    def has_add_permission(self, request, obj=None):
        return is_super_admin(request)

    def has_delete_permission(self, request, obj=None):
        return is_super_admin(request)


class ModelStaffAndSuperAdmin(admin.ModelAdmin):
    """
    admin and super-admin have permissions to edit, add,
    delete and see objs of the model
    """

    def has_module_permission(self, request, obj=None):
        return is_super_admin(request) or is_staff_admin(request)

    def has_change_permission(self, request, obj=None):
        return is_super_admin(request) or is_staff_admin(request)

    def has_view_permission(self, request, obj=None):
        return is_super_admin(request) or is_staff_admin(request)

    def has_add_permission(self, request, obj=None):
        return is_super_admin(request) or is_staff_admin(request)

    def has_delete_permission(self, request, obj=None):
        return is_super_admin(request) or is_staff_admin(request)


class ModelNoEditableAdmin(admin.ModelAdmin):
    """
    the model is not editable
    admin has permissions to see objs of the model
    super-admin have permissions to add, delete and see objs of the model
    """

    def has_module_permission(self, request, obj=None):
        return is_super_admin(request) or is_staff_admin(request)

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return is_super_admin(request) or is_staff_admin(request)

    def has_add_permission(self, request, obj=None):
        return is_super_admin(request)

    def has_delete_permission(self, request, obj=None):
        return is_super_admin(request)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            if not is_super_admin(request):
                del actions["delete_selected"]
        return actions


class ModelOnlyEditableSuperAdmin(admin.ModelAdmin):
    """
    admin has permissions to see objs of the model
    super-admin have permissions to edit, add, delete and see objs of the model
    """

    def has_module_permission(self, request, obj=None):
        return is_super_admin(request) or is_staff_admin(request)

    def has_change_permission(self, request, obj=None):
        return is_super_admin(request)

    def has_view_permission(self, request, obj=None):
        return is_super_admin(request) or is_staff_admin(request)

    def has_add_permission(self, request, obj=None):
        return is_super_admin(request)

    def has_delete_permission(self, request, obj=None):
        return is_super_admin(request)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            if not is_super_admin(request):
                del actions["delete_selected"]
        return actions

