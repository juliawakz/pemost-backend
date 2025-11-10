from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.services import MessagingService
from fcm_django.models import FCMDevice

User = get_user_model()


class Command(BaseCommand):
    help = 'Test push notification sending'

    def add_arguments(self, parser):
        parser.add_argument(
            'user_id', type=int, help='User ID to send test notification'
        )
        parser.add_argument(
            '--title', type=str, default='Test Notification',
            help='Notification title'
        )
        parser.add_argument(
            '--body', type=str, default='This is a test message',
            help='Notification body'
        )
        parser.add_argument(
            '--image', type=str, default=None,
            help='Image URL for notification'
        )

    def handle(self, *args, **options):
        user_id = options['user_id']
        title = options['title']
        body = options['body']
        image_url = options['image']

        try:
            user = User.objects.get(id=user_id)
            self.stdout.write(f"Sending notification to: {user.email}")

            # Check devices
            devices = FCMDevice.objects.filter(user=user, active=True)
            self.stdout.write(f"Active devices: {devices.count()}")

            if devices.count() == 0:
                self.stdout.write(
                    self.style.WARNING("User has no active devices registered")
                )
                return

            for device in devices:
                self.stdout.write(
                    f"  - {device.type}: {device.device_id} ({device.name})"
                )

            # Send notification
            self.stdout.write("\nSending notification...")
            result = MessagingService.send_push_notification(
                user_id=user_id,
                title=title,
                body=body,
                data={"test": "true", "timestamp": str(user.created_at)},
                image_url=image_url
            )

            if result['success']:
                msg = (
                    f"\nNotification sent successfully to "
                    f"{result['successful']}/{result['total_devices']} devices"
                )
                self.stdout.write(self.style.SUCCESS(msg))
            else:
                error = result.get('error')
                self.stdout.write(
                    self.style.ERROR(
                        f"\nFailed to send notification: {error}"
                    )
                )

            # Show detailed results
            if 'results' in result:
                self.stdout.write("\nDetailed Results:")
                for device_result in result['results']:
                    status = "Success" if device_result['success'] else "Failed"
                    self.stdout.write(
                        f"  {status} {device_result['type']}: {device_result['device_id']}"
                    )
                    if not device_result['success']:
                        error_msg = device_result.get('error', 'Unknown error')
                        self.stdout.write(
                            self.style.ERROR(f"    Error: {error_msg}")
                        )

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"User with ID {user_id} not found")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Unexpected error: {str(e)}")
            )
