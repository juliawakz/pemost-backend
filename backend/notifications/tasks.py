import asyncio

import firebase_admin
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth import get_user_model
from fcm_django.models import FCMDevice
from firebase_admin import credentials, messaging
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
        user_id, notification_title, notification_msg):
    try:
        user = User.objects.get(id=user_id)
        devices = FCMDevice.objects.filter(user=user, active=True)
        for device in devices:
            device.send_message(
                message=messaging.Message(
                    notification=messaging.Notification(
                        title=notification_title,
                        body=notification_msg
                    ),
                    token=device.registration_id
                )
            )
        return {'success': True, 'message': 'Notification sent successfully'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
