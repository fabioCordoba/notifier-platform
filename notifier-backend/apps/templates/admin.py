from django.contrib import admin
from .models import Template


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'channel', 'organization', 'is_active', 'created_at')
    list_filter = ('channel', 'is_active', 'organization')
    search_fields = ('name',)
