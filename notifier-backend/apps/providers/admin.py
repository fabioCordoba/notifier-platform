from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Provider


class ProviderAdminForm(forms.ModelForm):
    config_json = forms.JSONField(
        label='Configuración (JSON)',
        required=True,
        widget=forms.Textarea(attrs={
            'rows': 12,
            'style': 'font-family:monospace;width:100%;',
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

        elif name == Provider.Name.TWILIO:
            required = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_FROM_NUMBER']
            missing = [k for k in required if not data.get(k)]
            if missing:
                raise ValidationError(f"Faltan campos requeridos para Twilio: {', '.join(missing)}")

        elif name == Provider.Name.FIREBASE:
            required = ['type', 'project_id', 'private_key', 'client_email']
            missing = [k for k in required if not data.get(k)]
            if missing:
                raise ValidationError(
                    f"Faltan campos del Service Account de Firebase: {', '.join(missing)}"
                )

        elif name == Provider.Name.CHATWOOT:
            required = ['CHATWOOT_BASE_URL', 'CHATWOOT_ACCOUNT_ID', 'CHATWOOT_INBOX_ID', 'CHATWOOT_API_TOKEN']
            missing = [k for k in required if not data.get(k)]
            if missing:
                raise ValidationError(f"Faltan campos requeridos para Chatwoot: {', '.join(missing)}")

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
