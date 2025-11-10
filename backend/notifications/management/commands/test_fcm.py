from django.core.management.base import BaseCommand
from fcm_django.models import FCMDevice
from django.contrib.auth import get_user_model
from firebase_admin.messaging import Message
from firebase_admin.messaging import Notification as FCMNotification

User = get_user_model()


class Command(BaseCommand):
    help = 'Send a test FCM push notification to a user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to send notification to',
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username to send notification to',
        )
        parser.add_argument(
            '--title',
            type=str,
            default='Test Notification',
            help='Notification title',
        )
        parser.add_argument(
            '--body',
            type=str,
            default='This is a test notification from Django',
            help='Notification body',
        )
        parser.add_argument(
            '--all-devices',
            action='store_true',
            help='Send to all registered devices',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        username = options.get('username')
        title = options['title']
        body = options['body']
        all_devices = options['all_devices']

        if all_devices:
            devices = FCMDevice.objects.filter(active=True)
            self.stdout.write(f"Sending to all active devices ({devices.count()})...")
        elif user_id:
            try:
                user = User.objects.get(id=user_id)
                devices = FCMDevice.objects.filter(user=user, active=True)
                self.stdout.write(f"Sending to devices for user ID {user_id} ({devices.count()})...")
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with ID {user_id} does not exist'))
                return
        elif username:
            try:
                user = User.objects.get(username=username)
                devices = FCMDevice.objects.filter(user=user, active=True)
                self.stdout.write(f"Sending to devices for username {username} ({devices.count()})...")
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with username {username} does not exist'))
                return
        else:
            self.stdout.write(self.style.ERROR('Please provide --user-id, --username, or --all-devices'))
            return

        if not devices.exists():
            self.stdout.write(self.style.WARNING('No active devices found'))
            return

        try:
            # Construct FCM message
            message = Message(
                notification=FCMNotification(
                    title=title,
                    body=body
                ),
                data={"test": "true", "source": "management_command"}
            )

            result = devices.send_message(message)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully sent notification to {devices.count()} device(s)'
                )
            )

            # Handle different response types
            if hasattr(result, 'success_count'):
                self.stdout.write(
                    f'Success: {result.success_count}, '
                    f'Failures: {result.failure_count}'
                )
            elif isinstance(result, dict):
                self.stdout.write(f'Result: {result}')
            else:
                self.stdout.write(f'Message ID: {result}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error sending notification: {str(e)}')
            )
