from django.template.loader import render_to_string

from apps.core.tasks import send_email_task


def send_notification(to_email, title, message, detail=None):
    """
    Envía una notificación del sistema por email de forma asíncrona (Celery).

    Args:
        to_email: str o lista de str con destinatario(s)
        title: asunto y título principal del correo
        message: párrafo principal
        detail: texto opcional en caja resaltada
    """
    html_content = render_to_string("email/notification.html", {
        "title": title,
        "message": message,
        "detail": detail,
    })
    return send_email_task.delay(
        to_email=to_email,
        subject=title,
        plain_content=message,
        html_content=html_content,
    )
