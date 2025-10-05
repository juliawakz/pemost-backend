from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.models import Notification
from notifications.tasks import send_fb_push_notification, send_notification_via_push


@receiver(post_save, sender=Notification)
def send_notification(
        sender, instance: Notification, created, *args, **kwargs):
    if created:
        send_notification_via_push.delay(
            msg={
                "message": instance.message,
                "id": instance.id.hex,
                "read": instance.is_read,
                "time": instance.created_at,
                "destine": instance.message_to.full_name,
            },
            channel=instance.channel,
        )

        send_fb_push_notification.delay(
            user_id=instance.message_to.id,
            notification_title="New Pemost message!!!",
            notification_msg=instance.message
        )
