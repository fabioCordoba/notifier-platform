import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_notification(self, notification_id: str):
    from apps.notifications.models import Notification, DeliveryAttempt

    try:
        notification = Notification.objects.select_related("organization").get(id=notification_id)
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} no encontrada.")
        return

    notification.status = Notification.Status.PROCESSING
    notification.save(update_fields=["status", "updated_at"])

    channels = notification.channels or ["EMAIL"]

    TASK_MAP = {
        "EMAIL": send_email_task,
        "SMS": send_sms_task,
        "WHATSAPP": send_whatsapp_task,
        "PUSH": send_push_task,
        "WEBSOCKET": send_websocket_task,
        "INAPP": send_websocket_task,
    }

    for recipient in notification.recipients.all():
        for channel in channels:
            attempt, created = DeliveryAttempt.objects.get_or_create(
                recipient=recipient,
                channel=channel,
                attempt_number=1,
                defaults={"status": DeliveryAttempt.Status.QUEUED},
            )
            if not created and attempt.status not in (
                DeliveryAttempt.Status.PENDING,
                DeliveryAttempt.Status.FAILED,
            ):
                continue

            task = TASK_MAP.get(channel)
            if task:
                task.delay(str(attempt.id))
            else:
                logger.warning(f"Canal {channel} no tiene worker asignado.")


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def send_email_task(self, attempt_id: str):
    from apps.notifications.models import DeliveryAttempt
    from apps.delivery.registry import get_channel

    try:
        attempt = DeliveryAttempt.objects.select_related(
            "recipient__notification__organization",
            "recipient__notification__template",
        ).get(id=attempt_id)
    except DeliveryAttempt.DoesNotExist:
        logger.error(f"DeliveryAttempt {attempt_id} no encontrado.")
        return

    success = get_channel("EMAIL").send(attempt)
    if not success and self.request.retries < self.max_retries:
        raise self.retry(countdown=120 * (self.request.retries + 1))
    _update_notification_status(str(attempt.recipient.notification_id))


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_sms_task(self, attempt_id: str):
    from apps.notifications.models import DeliveryAttempt
    from apps.delivery.registry import get_channel

    try:
        attempt = DeliveryAttempt.objects.select_related(
            "recipient__notification__organization",
            "recipient__notification__template",
        ).get(id=attempt_id)
    except DeliveryAttempt.DoesNotExist:
        logger.error(f"DeliveryAttempt {attempt_id} no encontrado.")
        return

    success = get_channel("SMS").send(attempt)
    if not success and self.request.retries < self.max_retries:
        raise self.retry(countdown=60 * (self.request.retries + 1))
    _update_notification_status(str(attempt.recipient.notification_id))


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_whatsapp_task(self, attempt_id: str):
    from apps.notifications.models import DeliveryAttempt
    from apps.delivery.registry import get_channel

    try:
        attempt = DeliveryAttempt.objects.select_related(
            "recipient__notification__organization",
            "recipient__notification__template",
        ).get(id=attempt_id)
    except DeliveryAttempt.DoesNotExist:
        logger.error(f"DeliveryAttempt {attempt_id} no encontrado.")
        return

    success = get_channel("WHATSAPP").send(attempt)
    if not success and self.request.retries < self.max_retries:
        raise self.retry(countdown=60 * (self.request.retries + 1))
    _update_notification_status(str(attempt.recipient.notification_id))


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_push_task(self, attempt_id: str):
    from apps.notifications.models import DeliveryAttempt
    from apps.delivery.registry import get_channel

    try:
        attempt = DeliveryAttempt.objects.select_related(
            "recipient__notification__organization",
        ).get(id=attempt_id)
    except DeliveryAttempt.DoesNotExist:
        logger.error(f"DeliveryAttempt {attempt_id} no encontrado.")
        return

    success = get_channel("PUSH").send(attempt)
    if not success and self.request.retries < self.max_retries:
        raise self.retry(countdown=30 * (self.request.retries + 1))
    _update_notification_status(str(attempt.recipient.notification_id))


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def send_websocket_task(self, attempt_id: str):
    from apps.notifications.models import DeliveryAttempt
    from apps.delivery.registry import get_channel

    try:
        attempt = DeliveryAttempt.objects.select_related(
            "recipient__notification__organization",
        ).get(id=attempt_id)
    except DeliveryAttempt.DoesNotExist:
        logger.error(f"DeliveryAttempt {attempt_id} no encontrado.")
        return

    get_channel("WEBSOCKET").send(attempt)
    _update_notification_status(str(attempt.recipient.notification_id))


@shared_task
def process_scheduled_notifications():
    from apps.notifications.models import Notification
    due = Notification.objects.filter(
        status=Notification.Status.QUEUED,
        scheduled_at__lte=timezone.now(),
        scheduled_at__isnull=False,
    )
    for notification in due:
        process_notification.delay(str(notification.id))


def _update_notification_status(notification_id: str):
    from apps.notifications.models import Notification, DeliveryAttempt

    try:
        notification = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        return

    attempts = DeliveryAttempt.objects.filter(recipient__notification=notification)
    if not attempts.exists():
        return

    statuses = set(attempts.values_list("status", flat=True))
    terminal = {DeliveryAttempt.Status.SENT, DeliveryAttempt.Status.DELIVERED,
                DeliveryAttempt.Status.READ, DeliveryAttempt.Status.FAILED,
                DeliveryAttempt.Status.CANCELLED}

    if not statuses.issubset(terminal):
        return

    if statuses == {DeliveryAttempt.Status.FAILED}:
        notification.status = Notification.Status.FAILED
    elif DeliveryAttempt.Status.FAILED in statuses:
        notification.status = Notification.Status.PARTIALLY_FAILED
    else:
        notification.status = Notification.Status.COMPLETED

    notification.save(update_fields=["status", "updated_at"])
