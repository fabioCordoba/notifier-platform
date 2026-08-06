from django.contrib import admin
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, reverse
from django.utils.html import format_html
from .models import Organization, ApiKey


class ApiKeyInline(admin.TabularInline):
    model = ApiKey
    extra = 0
    can_delete = True
    show_change_link = True
    readonly_fields = ('key_prefix', 'key_hash', 'last_used_at', 'created_at', 'is_active')
    fields = ('name', 'key_prefix', 'is_active', 'last_used_at', 'expires_at', 'created_at')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan', 'active_keys_count', 'is_active', 'created_at')
    list_filter = ('plan', 'is_active')
    search_fields = ('name',)
    inlines = [ApiKeyInline]
    readonly_fields = ('generate_key_button',)

    def get_fields(self, request, obj=None):
        fields = ['name', 'logo', 'plan', 'is_active']
        if obj:
            fields.append('generate_key_button')
        return fields

    @admin.display(description='Keys activas')
    def active_keys_count(self, obj):
        return obj.api_keys.filter(is_active=True).count()

    @admin.display(description='')
    def generate_key_button(self, obj):
        url = reverse('admin:org-generate-key', args=[obj.pk])
        return format_html(
            '<a class="button" href="{}" style="padding:6px 12px;background:#417690;'
            'color:#fff;border-radius:4px;text-decoration:none;font-size:13px;">'
            '+ Generar nueva API Key</a>',
            url,
        )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                '<uuid:org_id>/generate-key/',
                self.admin_site.admin_view(self.generate_key_view),
                name='org-generate-key',
            ),
        ]
        return custom + urls

    def generate_key_view(self, request, org_id):
        org = get_object_or_404(Organization, pk=org_id)
        instance, raw_key = ApiKey.generate(organization=org, name='Generada desde Admin')
        self.message_user(
            request,
            format_html(
                '<strong>{}</strong> — nueva API Key: <code style="font-size:13px">{}</code> '
                '&nbsp;(prefijo: <code>{}</code>). '
                '<strong>Cópiala ahora, no se mostrará de nuevo.</strong>',
                org.name,
                raw_key,
                instance.key_prefix,
            ),
        )
        return redirect(f'../{org_id}/change/')


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'key_prefix', 'organization', 'is_active', 'last_used_at', 'expires_at', 'created_at')
    list_filter = ('is_active', 'organization')
    search_fields = ('name', 'key_prefix', 'organization__name')
    readonly_fields = ('key_hash', 'key_prefix', 'last_used_at', 'created_at')
    fields = ('organization', 'name', 'key_prefix', 'key_hash', 'is_active', 'expires_at', 'last_used_at', 'created_at')
    actions = ['revoke_keys']

    def has_add_permission(self, request):
        return False

    @admin.action(description='Revocar keys seleccionadas')
    def revoke_keys(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} key(s) revocada(s).')
