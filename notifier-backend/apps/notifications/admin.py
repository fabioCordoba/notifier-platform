from django.contrib import admin
from .models import Notification, Recipient, DeliveryAttempt


class RecipientInline(admin.TabularInline):
    model = Recipient
    extra = 0
    readonly_fields = ('created_at',)


class DeliveryAttemptInline(admin.TabularInline):
    model = DeliveryAttempt
    extra = 0
    readonly_fields = ('created_at', 'updated_at', 'sent_at', 'delivered_at', 'read_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'organization')
    search_fields = ('title',)
    inlines = [RecipientInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'app_user_id', 'notification')
    inlines = [DeliveryAttemptInline]


@admin.register(DeliveryAttempt)
class DeliveryAttemptAdmin(admin.ModelAdmin):
    list_display = ('channel', 'provider', 'status', 'recipient', 'sent_at', 'created_at')
    list_filter = ('channel', 'status')
    readonly_fields = ('created_at', 'updated_at', 'sent_at', 'delivered_at', 'read_at')
