from django.contrib import admin
from .models import Organization, ApiKey


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan', 'is_active', 'created_at')
    list_filter = ('plan', 'is_active')
    search_fields = ('name',)


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'key_prefix', 'organization', 'is_active', 'last_used_at', 'created_at')
    list_filter = ('is_active', 'organization')
    search_fields = ('name', 'key_prefix')
    readonly_fields = ('key_hash', 'key_prefix', 'last_used_at', 'created_at')
