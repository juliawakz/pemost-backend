from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from fcm_django.models import FCMDevice
from django.db.models import Count, Q

User = get_user_model()


class Command(BaseCommand):
    help = 'List all FCM devices and notification statistics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=int,
            help='Filter by user ID'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['ios', 'android', 'web'],
            help='Filter by device type'
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show statistics only'
        )

    def handle(self, *args, **options):
        user_id = options.get('user')
        device_type = options.get('type')
        show_stats = options.get('stats')

        # Base queryset
        devices = FCMDevice.objects.all()

        # Apply filters
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                devices = devices.filter(user=user)
                self.stdout.write(f"Filtering by user: {user.email}\n")
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"User with ID {user_id} not found")
                )
                return

        if device_type:
            devices = devices.filter(type=device_type)

        # Show statistics
        if show_stats:
            self._show_statistics()
            return

        # List devices
        total = devices.count()
        active = devices.filter(active=True).count()

        self.stdout.write(f"Total devices: {total}")
        self.stdout.write(f"Active devices: {active}\n")

        if total == 0:
            self.stdout.write(
                self.style.WARNING("No devices found")
            )
            return

        # Group by user
        users_with_devices = devices.values('user').distinct()

        for user_data in users_with_devices:
            try:
                user = User.objects.get(id=user_data['user'])
                user_devices = devices.filter(user=user)

                self.stdout.write(
                    self.style.SUCCESS(f"\n{user.email} (ID: {user.id})")
                )

                for device in user_devices:
                    status = "Active" if device.active else "Inactive"
                    self.stdout.write(
                        f"  [{device.type.upper()}] {device.name or device.device_id}"
                    )
                    self.stdout.write(f"    Status: {status}")
                    self.stdout.write(f"    Device ID: {device.device_id}")
                    self.stdout.write(
                        f"    Token: {device.registration_id[:30]}..."
                        if len(device.registration_id) > 30
                        else f"    Token: {device.registration_id}"
                    )
                    if device.date_created:
                        self.stdout.write(f"    Registered: {device.date_created}")

            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"  User ID {user_data['user']} (deleted)")
                )

    def _show_statistics(self):
        """Show overall statistics"""
        from notifications.models import Notification

        self.stdout.write(self.style.SUCCESS("=== DEVICE STATISTICS ===\n"))

        # Device stats by type
        device_stats = FCMDevice.objects.values('type').annotate(
            total=Count('id'),
            active=Count('id', filter=Q(active=True)),
            inactive=Count('id', filter=Q(active=False))
        ).order_by('type')

        if device_stats:
            self.stdout.write("Devices by Type:")
            for stat in device_stats:
                self.stdout.write(
                    f"  {stat['type'].upper()}: {stat['total']} total "
                    f"({stat['active']} active, {stat['inactive']} inactive)"
                )
        else:
            self.stdout.write("  No devices registered")

        # Users with devices
        users_with_devices = FCMDevice.objects.values('user').distinct().count()
        total_users = User.objects.count()

        self.stdout.write(
            f"\nUsers: {users_with_devices}/{total_users} have registered devices "
            f"({users_with_devices/total_users*100:.1f}%)" if total_users > 0 else "\nNo users"
        )

        # Notification stats
        self.stdout.write(self.style.SUCCESS("\n=== NOTIFICATION STATISTICS ===\n"))

        notification_stats = Notification.objects.filter(
            message_type='PUSH'
        ).aggregate(
            total=Count('id'),
            read=Count('id', filter=Q(is_read=True)),
            unread=Count('id', filter=Q(is_read=False))
        )

        self.stdout.write(
            f"Push Notifications: {notification_stats['total']} total "
            f"({notification_stats['read']} read, {notification_stats['unread']} unread)"
        )

        # Recent notifications
        recent = Notification.objects.filter(
            message_type='PUSH'
        ).order_by('-created_at')[:5]

        if recent.exists():
            self.stdout.write("\nRecent Notifications:")
            for notif in recent:
                status = "Read" if notif.is_read else "Unread"
                self.stdout.write(
                    f"  {status} [{notif.created_at.strftime('%Y-%m-%d %H:%M')}] "
                    f"{notif.subject} → {notif.message_to.email}"
                )
