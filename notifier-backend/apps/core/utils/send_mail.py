from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_email(to_email, subject, plain_content, html_content=None):
    recipients = [to_email] if isinstance(to_email, str) else to_email
    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
    )
    if html_content:
        email.attach_alternative(html_content, "text/html")
    try:
        email.send()
        return {"status": "sent"}
    except Exception as e:
        return {"error": str(e)}
