import asyncio

import firebase_admin
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth import get_user_model
from firebase_admin import credentials
from notifications.choices import MessageTypeChoices
from notifications.models import Notification
from notifications.services import MessagingService
from project.celery import app

User = get_user_model()

cred = credentials.Certificate(f"{settings.BASE_DIR}/firebasefile.json")

firebase_admin.initialize_app(cred)


@app.task
def send_email_task(
        to, from_email, subject, msg=None, html_content=None, sender=None):
    if sender:
        user = User.objects.get(email=sender)
    else:
        user = User.objects.get(email=to)

    payload = {
        "channel": MessageTypeChoices.EMAIL,
        "subject": subject,
        "message_type": MessageTypeChoices.EMAIL,
        "message_to": user,
        "message": subject
    }

    Notification.objects.create(**payload)

    MessagingService.send_email(to, from_email, subject, msg, html_content)


@app.task
def send_notification_via_push(msg, channel):
    channel_layer = get_channel_layer()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(channel_layer.group_send(
        f"{channel}", {"type": "send_notification", "message": msg}
    ))
    return "Done"


@app.task
def send_fb_push_notification(
        user_id, notification_title, notification_msg, data=None, image_url=None):
    """
    Celery task to send push notification to a user.

    :param user_id: User ID to send notification to
    :param notification_title: Title of the notification
    :param notification_msg: Body text of the notification
    :param data: Optional dict of custom data
    :param image_url: Optional image URL for rich notifications
    :return: Dict with success status and results
    """
    return MessagingService.send_push_notification(
        user_id=user_id,
        title=notification_title,
        body=notification_msg,
        data=data,
        image_url=image_url
    )


@app.task
def send_data_notification(user_id, data):
    """
    Celery task to send data-only (silent) notification to a user.

    :param user_id: User ID to send notification to
    :param data: Dict of data to send
    :return: Dict with success status and results
    """
    return MessagingService.send_data_message(user_id=user_id, data=data)
