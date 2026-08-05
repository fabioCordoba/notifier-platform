from django.contrib import admin
from .models import Provider


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'channel', 'organization', 'is_default', 'is_active', 'created_at')
    list_filter = ('channel', 'name', 'is_active', 'is_default')
    readonly_fields = ('created_at', 'updated_at')
