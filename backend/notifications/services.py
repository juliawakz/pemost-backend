import logging

from decouple import config
from django.contrib.auth import get_user_model
from fcm_django.models import FCMDevice
from firebase_admin import messaging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Mail

logger = logging.getLogger(__file__)
User = get_user_model()


class MessagingService:
    @staticmethod
    def send_email(to, from_email, subject, msg=None, html_content=None):
        """
        Sends an email with plain text and/or HTML content using SendGrid.
        :param to: Recipient email (str or list of str)
        :param from_email: Sender email (str)
        :param subject: Email subject (str)
        :param msg: Plain text message (str, optional)
        :param html_content: HTML message (str, optional)
        """
        if not msg and not html_content:
            logger.warning("No message content provided for email")
            return

        # Create Mail object
        message = Mail(
            from_email=from_email,
            to_emails=to,
            subject=subject,
        )

        # Prefer plain text as fallback if both exist
        if msg:
            message.add_content(Content("text/plain", msg))

        if html_content:
            message.add_content(Content("text/html", html_content))

        try:
            sg = SendGridAPIClient(config('SENDGRID_API_KEY'))
            response = sg.send(message)
            logger.info(
                "Email sent to %s, status: %s", to, response.status_code)
            return response
        except Exception as e:
            logger.error("Error sending email: %s", e, exc_info=True)
            return None

    @staticmethod
    def send_push_notification(
        user_id,
        title,
        body,
        data=None,
        image_url=None,
        sound="default"
    ):
        """
        Send push notification to all active devices of a user.

        :param user_id: User ID to send notification to
        :param title: Notification title
        :param body: Notification body text
        :param data: Optional dict of custom data to send with notification
        :param image_url: Optional image URL for rich notifications
        :param sound: Notification sound (default: "default")
        :return: Dict with success status and results
        """
        try:
            user = User.objects.get(id=user_id)
            devices = FCMDevice.objects.filter(user=user, active=True)

            if not devices.exists():
                logger.warning(f"No active devices found for user {user_id}")
                return {
                    'success': False,
                    'error': 'No active devices found'
                }

            results = []
            for device in devices:
                try:
                    # Build notification
                    notification = messaging.Notification(
                        title=title,
                        body=body,
                        image=image_url
                    )

                    # Build message
                    message = messaging.Message(
                        notification=notification,
                        data=data or {},
                        token=device.registration_id,
                        android=messaging.AndroidConfig(
                            priority='high',
                            notification=messaging.AndroidNotification(
                                sound=sound,
                                priority='high'
                            )
                        ),
                        apns=messaging.APNSConfig(
                            payload=messaging.APNSPayload(
                                aps=messaging.Aps(
                                    sound=sound,
                                    badge=1
                                )
                            )
                        )
                    )

                    # Send message
                    response = device.send_message(message=message)
                    results.append({
                        'device_id': device.device_id,
                        'type': device.type,
                        'success': True,
                        'response': response
                    })
                    logger.info(
                        f"Push notification sent to device {device.device_id} "
                        f"for user {user_id}"
                    )

                except Exception as device_error:
                    logger.error(
                        f"Error sending to device {device.device_id}: "
                        f"{device_error}",
                        exc_info=True
                    )
                    results.append({
                        'device_id': device.device_id,
                        'type': device.type,
                        'success': False,
                        'error': str(device_error)
                    })

            # Return overall success if at least one device succeeded
            success = any(r['success'] for r in results)
            return {
                'success': success,
                'results': results,
                'total_devices': len(devices),
                'successful': sum(1 for r in results if r['success'])
            }

        except User.DoesNotExist:
            logger.error(f"User {user_id} not found")
            return {'success': False, 'error': 'User not found'}
        except Exception as e:
            logger.error(f"Error sending push notification: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    @staticmethod
    def send_data_message(user_id, data):
        """
        Send a data-only message (silent notification) to user's devices.
        Useful for triggering background sync or updates.

        :param user_id: User ID to send message to
        :param data: Dict of data to send
        :return: Dict with success status and results
        """
        try:
            user = User.objects.get(id=user_id)
            devices = FCMDevice.objects.filter(user=user, active=True)

            if not devices.exists():
                logger.warning(f"No active devices found for user {user_id}")
                return {
                    'success': False,
                    'error': 'No active devices found'
                }

            results = []
            for device in devices:
                try:
                    message = messaging.Message(
                        data=data,
                        token=device.registration_id,
                        android=messaging.AndroidConfig(
                            priority='high'
                        ),
                        apns=messaging.APNSConfig(
                            headers={'apns-priority': '5'},
                            payload=messaging.APNSPayload(
                                aps=messaging.Aps(
                                    content_available=True
                                )
                            )
                        )
                    )

                    response = device.send_message(message=message)
                    results.append({
                        'device_id': device.device_id,
                        'type': device.type,
                        'success': True,
                        'response': response
                    })

                except Exception as device_error:
                    logger.error(
                        f"Error sending data message to device "
                        f"{device.device_id}: {device_error}",
                        exc_info=True
                    )
                    results.append({
                        'device_id': device.device_id,
                        'type': device.type,
                        'success': False,
                        'error': str(device_error)
                    })

            success = any(r['success'] for r in results)
            return {
                'success': success,
                'results': results,
                'total_devices': len(devices),
                'successful': sum(1 for r in results if r['success'])
            }

        except User.DoesNotExist:
            logger.error(f"User {user_id} not found")
            return {'success': False, 'error': 'User not found'}
        except Exception as e:
            logger.error(f"Error sending data message: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
