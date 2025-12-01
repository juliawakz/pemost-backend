from typing import List
from alerts.models import Alert
from app.models.farm import Farm
from app.choices import AlertStatusChoices
from django.contrib.auth import get_user_model
from notifications.tasks import send_fb_push_notification, send_email_task

User = get_user_model()


class AlertNotificationService:
    """Service to create alerts and send notifications based on preferences"""

    @staticmethod
    def create_alert_and_notify(
        farm: Farm,
        alert_type: str,
        notification_title: str = "Alert Notification",
        notification_message: str = "",
        email_subject: str = "Farm Alert"
    ) -> Alert:
        """
        Create an alert and send notifications based on user preferences.

        Args:
            farm: Farm instance
            alert_type: Alert type (RED, YELLOW, GREEN, NONE)
            notification_title: Title for push notification
            notification_message: Message for notifications
            email_subject: Subject for email

        Returns:
            Created Alert instance
        """
        # Create the alert
        alert = Alert.objects.create(
            farm=farm,
            alert_type=alert_type,
            read=False
        )

        # Send notifications based on user preferences
        farmer = farm.farmer
        if farmer:
            AlertNotificationService._send_notifications(
                user=farmer,
                title=notification_title,
                message=notification_message,
                email_subject=email_subject,
                alert=alert
            )

        return alert

    @staticmethod
    def bulk_create_alerts_and_notify(
        farms: List[Farm],
        alert_type: str,
        notification_title: str = "Alert Notification",
        notification_message: str = "",
        email_subject: str = "Farm Alert"
    ) -> List[Alert]:
        """
        Bulk create alerts and send notifications.

        Args:
            farms: List of Farm instances
            alert_type: Alert type (RED, YELLOW, GREEN, NONE)
            notification_title: Title for push notification
            notification_message: Message for notifications
            email_subject: Subject for email

        Returns:
            List of created Alert instances
        """
        alerts_to_create = []
        farmers_to_notify = {}

        for farm in farms:
            alert = Alert(
                farm=farm,
                alert_type=alert_type,
                read=False
            )
            alerts_to_create.append(alert)

            # Group alerts by farmer to avoid duplicate notifications
            if farm.farmer:
                if farm.farmer.id not in farmers_to_notify:
                    farmers_to_notify[farm.farmer.id] = farm.farmer

        # Bulk create alerts
        created_alerts = Alert.objects.bulk_create(alerts_to_create)

        # Send notifications to unique farmers
        for farmer in farmers_to_notify.values():
            AlertNotificationService._send_notifications(
                user=farmer,
                title=notification_title,
                message=notification_message,
                email_subject=email_subject
            )

        return created_alerts

    @staticmethod
    def _send_notifications(
        user: User,
        title: str,
        message: str,
        email_subject: str = None,
        alert: Alert = None
    ):
        """
        Send notifications based on user preferences.

        Args:
            user: User instance
            title: Notification title
            message: Notification message
            email_subject: Email subject line
            alert: Optional Alert instance for additional context
        """
        # Send push notification if enabled
        if user.enable_push_notifications:
            send_fb_push_notification.delay(
                user_id=user.id,
                notification_title=title,
                notification_msg=message,
                data={
                    'alert_id': str(alert.id) if alert else None,
                    'type': 'alert'
                }
            )

        # Send email notification if enabled and user has email
        if user.enable_email_notifications and user.email:
            email_body = f"""
            Hello {user.full_name},

            {message}

            Please log in to your account to view more details.

            Best regards,
            PEMOST Team
            """

            send_email_task.delay(
                to=user.email,
                from_email='noreply@pemost.com',
                subject=email_subject or title,
                msg=email_body
            )
