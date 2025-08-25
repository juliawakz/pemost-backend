from django.contrib.auth import get_user_model
from notifications.choices import MessageTypeChoices
from notifications.models import Notification
from notifications.services import MessagingService
from project.celery import app

User = get_user_model()


@app.task
def send_email_task(to, from_email, subject, msg=None, html_content=None, sender=None):
    if sender:
        user = User.objects.get(email=sender)
    else:
        user = User.objects.get(email=to)

    payload = {
        "channel": MessageTypeChoices.EMAIL,
        "subject": subject,
        "message_type": MessageTypeChoices.EMAIL,
        "message_to": user
    }

    if html_content:
        payload["message"] = html_content
    else:
        payload["message"] = msg

    Notification.objects.create(**payload)

    MessagingService.send_email(to, from_email, subject, msg, html_content)
