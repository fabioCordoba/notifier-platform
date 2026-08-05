from celery import shared_task

from apps.core.utils.send_mail import send_email


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, to_email, subject, plain_content, html_content=None):
    result = send_email(to_email, subject, plain_content, html_content)
    if "error" in result:
        raise self.retry(exc=Exception(result["error"]))
    return result
