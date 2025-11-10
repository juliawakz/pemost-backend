# Firebase Cloud Messaging (FCM) Testing Guide

This guide explains how to test FCM push notifications for your Android Ionic app before frontend integration.

## Prerequisites

1. Firebase project set up with FCM enabled
2. Firebase Admin SDK credentials configured in your project
3. Valid FCM device registration token from a test device

## Method 1: Using the Test API Endpoint (Easiest)

### Step 1: Register a Test Device

First, you need a valid FCM registration token. You can get this from:
- Firebase Console (see Method 4 below)
- A test Android device with your app
- Firebase SDK test tools

Register the device:

```bash
curl -X POST http://localhost:8000/api/notifications/register/device/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "registration_id": "YOUR_FCM_TOKEN_HERE",
    "name": "Test Android Device",
    "device_id": "test-device-001",
    "type": "android"
  }'
```

### Step 2: Send Test Notification

```bash
curl -X POST http://localhost:8000/api/notifications/test/push/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Hello from Backend!",
    "body": "This is a test notification",
    "data": {
      "type": "test",
      "timestamp": "2024-01-01"
    }
  }'
```

### Step 3: View Your Registered Devices

```bash
curl -X GET http://localhost:8000/api/notifications/devices/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Method 2: Using Django Management Command

### Send to Specific User by ID

```bash
python manage.py test_fcm --user-id 1 --title "Test" --body "Hello User!"
```

### Send to Specific User by Username

```bash
python manage.py test_fcm --username john@example.com --title "Test" --body "Hello John!"
```

### Send to All Devices (Broadcast)

```bash
python manage.py test_fcm --all-devices --title "Broadcast" --body "Hello Everyone!"
```

## Method 3: Using Python Script

Create a test script `test_notification.py`:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from fcm_django.models import FCMDevice
from django.contrib.auth import get_user_model

User = get_user_model()

# Get a test user
user = User.objects.first()  # or get a specific user
print(f"Testing for user: {user}")

# Get user's devices
devices = FCMDevice.objects.filter(user=user, active=True)
print(f"Found {devices.count()} active device(s)")

if devices.exists():
    # Send notification
    result = devices.send_message(
        title="Test from Script",
        body="This is a test notification sent from Python script",
        data={
            "type": "test",
            "custom_key": "custom_value"
        }
    )
    print(f"Notification sent! Result: {result}")
else:
    print("No active devices found")
```

Run it:

```bash
python test_notification.py
```

## Method 4: Using Firebase Console (No Backend Code Needed)

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Navigate to **Cloud Messaging** (in left sidebar)
4. Click **Send your first message** or **New notification**
5. Fill in:
   - **Notification title**: "Test Notification"
   - **Notification text**: "This is a test"
6. Click **Send test message**
7. Enter your FCM registration token
8. Click **Test**

### How to Get FCM Token for Testing:

**Option A: Use a test Android app**
```javascript
// In your Ionic/Capacitor app
import { PushNotifications } from '@capacitor/push-notifications';

PushNotifications.requestPermissions().then(result => {
  if (result.receive === 'granted') {
    PushNotifications.register();
  }
});

PushNotifications.addListener('registration', (token) => {
  console.log('Push registration success, token: ' + token.value);
  // Copy this token and use it for testing
});
```

**Option B: Use FCM API directly**
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Get a test token (requires Android SDK setup)
firebase messaging:test-token
```

## Method 5: Using Postman/Insomnia

### 1. Register Device

```
POST http://localhost:8000/api/notifications/register/device/
Headers:
  Authorization: Bearer YOUR_JWT_TOKEN
  Content-Type: application/json

Body:
{
  "registration_id": "YOUR_FCM_TOKEN",
  "name": "Postman Test Device",
  "device_id": "postman-test-001",
  "type": "android"
}
```

### 2. Send Test Notification

```
POST http://localhost:8000/api/notifications/test/push/
Headers:
  Authorization: Bearer YOUR_JWT_TOKEN
  Content-Type: application/json

Body:
{
  "title": "Test from Postman",
  "body": "Testing FCM notifications",
  "data": {
    "screen": "home",
    "action": "refresh"
  }
}
```

## Method 6: Using Django Shell

```bash
python manage.py shell
```

```python
from fcm_django.models import FCMDevice
from django.contrib.auth import get_user_model

User = get_user_model()

# Get a user
user = User.objects.get(id=1)  # or username="test@example.com"

# Create a test device registration
device = FCMDevice.objects.create(
    user=user,
    registration_id="YOUR_FCM_TOKEN_HERE",
    type="android",
    name="Test Device"
)

# Send a test notification
device.send_message(
    title="Test from Django Shell",
    body="This is a test notification",
    data={"test": True}
)

# Or send to all user devices
devices = FCMDevice.objects.filter(user=user, active=True)
devices.send_message(
    title="Broadcast to User",
    body="Sent to all devices"
)
```

## Testing with Ionic/Capacitor App (for Frontend Team)

When the frontend team is ready to integrate, they should:

### 1. Install Dependencies

```bash
npm install @capacitor/push-notifications
npx cap sync
```

### 2. Configure Firebase in Ionic App

Add `google-services.json` to `android/app/` directory

### 3. Request Permissions and Register Device

```typescript
import { PushNotifications } from '@capacitor/push-notifications';
import { HttpClient } from '@angular/common/http';

// Request permission
const permStatus = await PushNotifications.requestPermissions();

if (permStatus.receive === 'granted') {
  // Register with FCM
  await PushNotifications.register();
}

// Listen for registration token
PushNotifications.addListener('registration', (token) => {
  console.log('FCM Token:', token.value);

  // Send to your backend
  this.http.post('http://your-api.com/api/notifications/register/device/', {
    registration_id: token.value,
    name: 'My Android Device',
    device_id: device.uuid,  // from @capacitor/device
    type: 'android'
  }, {
    headers: {
      Authorization: `Bearer ${yourJWTToken}`
    }
  }).subscribe();
});

// Listen for notifications
PushNotifications.addListener('pushNotificationReceived', (notification) => {
  console.log('Push received:', notification);
});

PushNotifications.addListener('pushNotificationActionPerformed', (notification) => {
  console.log('Push action performed:', notification);
});
```

## Troubleshooting

### No devices registered
- Check that the FCM token is valid
- Verify user authentication
- Check device registration API response

### Notifications not received
- Verify Firebase Admin SDK is properly configured
- Check Firebase service account credentials
- Ensure FCM is enabled in Firebase Console
- Verify the FCM token hasn't expired
- Check device is active: `FCMDevice.objects.filter(active=True)`

### Permission denied
- Ensure user is authenticated
- Check JWT token is valid
- Verify Authorization header format: `Bearer <token>`

### View FCM Logs

```bash
# In Django shell
from fcm_django.models import FCMDevice

# List all devices
for device in FCMDevice.objects.all():
    print(f"User: {device.user}, Token: {device.registration_id[:20]}..., Active: {device.active}")
```

## Production Considerations

⚠️ **Important:** Remove or restrict the `test/push` endpoint before deploying to production!

```python
# In viewsets.py, add permission check:
from django.conf import settings

@action(detail=False, methods=["post"], url_path="test/push")
def test_push_notification(self, request):
    # Only allow in debug mode
    if not settings.DEBUG:
        return Response(
            {"detail": "This endpoint is only available in debug mode"},
            status=status.HTTP_403_FORBIDDEN
        )
    # ... rest of the code
```

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/notifications/register/device/` | POST | Register FCM device |
| `/api/notifications/unregister/device/` | POST | Unregister FCM device |
| `/api/notifications/devices/` | GET | List user's devices |
| `/api/notifications/test/push/` | POST | Send test notification (dev only) |

## Next Steps

1. Get a valid FCM token from a test device
2. Use Method 1 to register and test
3. Verify notifications are received on the device
4. Share the registration endpoint with frontend team
5. Frontend team integrates using the Ionic/Capacitor example above
