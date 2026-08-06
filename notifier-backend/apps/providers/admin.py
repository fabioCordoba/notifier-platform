import json
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Provider


SMTP_HELP = (
    '{\n'
    '  "EMAIL_HOST": "mail.tudominio.com",\n'
    '  "EMAIL_PORT": 465,\n'
    '  "EMAIL_USE_TLS": false,\n'
    '  "EMAIL_USE_SSL": true,\n'
    '  "EMAIL_HOST_USER": "notificaciones@tudominio.com",\n'
    '  "EMAIL_HOST_PASSWORD": "your_email_password",\n'
    '  "DEFAULT_FROM_EMAIL": "Notifier <notificaciones@tudominio.com>"\n'
    '}'
)

SENDGRID_HELP = (
    '{\n'
    '  "api_key": "SG.xxxxxxxxxxxx",\n'
    '  "DEFAULT_FROM_EMAIL": "Notifier <notificaciones@tudominio.com>"\n'
    '}'
)


class ProviderAdminForm(forms.ModelForm):
    config_json = forms.JSONField(
        label='Configuración (JSON)',
        required=True,
        widget=forms.Textarea(attrs={
            'rows': 10,
            'style': 'font-family:monospace;width:100%;',
            'placeholder': SMTP_HELP,
        }),
    )

    class Meta:
        model = Provider
        fields = ['organization', 'channel', 'name', 'is_default', 'is_active', 'config_json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            try:
                self.fields['config_json'].initial = self.instance.get_config()
            except Exception:
                self.fields['config_json'].initial = {}

    def clean_config_json(self):
        data = self.cleaned_data.get('config_json', {})
        name = self.cleaned_data.get('name')

        if name == Provider.Name.SMTP:
            required = ['EMAIL_HOST', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD']
            missing = [k for k in required if not data.get(k)]
            if missing:
                raise ValidationError(f"Faltan campos requeridos para SMTP: {', '.join(missing)}")

            if data.get('EMAIL_USE_TLS') and data.get('EMAIL_USE_SSL'):
                raise ValidationError("EMAIL_USE_TLS y EMAIL_USE_SSL no pueden estar activos al mismo tiempo.")

            data.setdefault('EMAIL_PORT', 587)
            data.setdefault('EMAIL_USE_TLS', False)
            data.setdefault('EMAIL_USE_SSL', False)
            data.setdefault('DEFAULT_FROM_EMAIL', data['EMAIL_HOST_USER'])

        elif name == Provider.Name.SENDGRID:
            if not data.get('api_key'):
                raise ValidationError("SendGrid requiere el campo 'api_key'.")
            data.setdefault('DEFAULT_FROM_EMAIL', 'no-reply@notifier.io')

        return data


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    form = ProviderAdminForm
    list_display = ('name', 'channel', 'organization', 'is_default', 'is_active', 'created_at')
    list_filter = ('channel', 'name', 'is_active', 'is_default')
    readonly_fields = ('config_encrypted', 'created_at', 'updated_at')
    fields = ('organization', 'channel', 'name', 'config_json', 'is_default', 'is_active', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        obj.set_config(form.cleaned_data['config_json'])
        super().save_model(request, obj, form, change)
