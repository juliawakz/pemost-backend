# PeMost Backend

A comprehensive agricultural management system built with Django REST Framework and PostGIS for spatial data handling. PeMost provides APIs for farm management, crop tracking, pest control, and location-based services.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Data Loading](#data-loading)
- [Running the Application](#running-the-application)
- [Management Commands](#management-commands)
- [Push Notifications](#push-notifications)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Features

- **Farm Management**: Create, update, and manage farms with spatial boundaries
- **Crop Management**: Track crops, varieties, and growth stages
- **Pest Control**: Monitor and manage pest control activities
- **Location Services**: County, subcounty, and ward-based location tracking
- **User Management**: Multi-role system (Farmers, Extension Officers, System Admins)
- **Push Notifications**: Firebase Cloud Messaging (FCM) integration
- **Spatial Data**: PostGIS-powered geographic queries and boundary management
- **REST API**: Comprehensive RESTful API built with Django REST Framework
- **Bulk Import**: Shapefile upload support for farm boundaries

## Technology Stack

- **Backend Framework**: Django 4.x
- **API Framework**: Django REST Framework
- **Database**: PostgreSQL with PostGIS extension
- **Task Queue**: Celery with Redis
- **Push Notifications**: Firebase Cloud Messaging (FCM)
- **Spatial Libraries**: GDAL, OGR
- **Python Version**: 3.12+

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.12 or higher
- PostgreSQL 13+ with PostGIS extension
- Redis server
- GDAL/OGR libraries
- Git

##### Install System Dependencies (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3-pip python3-venv postgresql postgresql-contrib postgis redis-server gdal-bin libgdal-dev
```

## Installation

##### 1. Clone the Repository

```bash
git clone repository-url
cd pemost_backend
```

##### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

##### 3. Install Dependencies

```bash
cd backend
pip install -r requirements/dev.txt # for development
```

## Environment Configuration

##### 1. Create Environment File

```bash
cp environments/env.dev .env  
# OR
touch .env
```

##### 2. Configure Environment Variables

Edit the `.env` file with your configuration:

```env
# Project Settings
PROJECT_NAME=PeMost
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE=postgres
POSTGRES_DB=pemost_db
POSTGRES_USER=your_db_username
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Firebase Configuration (for Push Notifications)
FIREBASE_CREDENTIALS_PATH=/backend/sample_data/firebase-credentials.json

# Area Conversion Factor
ACERAGE_CONVERT=0.000247105  # square meters to acres
```

Generate firebasefile.json using the instructions found here: [Firebase Quick Setup](#quick-setup)

##### 3. Generate Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Database Setup

##### 1. Create PostgreSQL Database

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE pemost_db;
CREATE USER your_db_username WITH PASSWORD 'your_db_password';
ALTER ROLE your_db_username SET client_encoding TO 'utf8';
ALTER ROLE your_db_username SET default_transaction_isolation TO 'read committed';
ALTER ROLE your_db_username SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE pemost_db TO your_db_username;

-- Enable PostGIS extension
\c pemost_db
CREATE EXTENSION postgis;
\q
```

##### 2. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

##### 3. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.


##### 4. Start Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

##### 5. Access Admin Interface

Navigate to `http://127.0.0.1:8000/admin` and log in with your superuser credentials.

##### 6. Start Celery Worker (for background tasks)

In a separate terminal:

```bash
celery -A project worker -l info
```

##### 7. Start Redis (if not running as service)

In a separate terminal:

```bash
redis-server
```
## Run project using Docker
1. Install Docker and Docker-Compose, if not installed, and check the version:
* docker compose
  ```sh
  docker compose version
  ```
* Change directory
  ```sh
  cd to pemost-backendv2
  ```

2. Build the project with docker-compose as
   ```sh
   docker compose -f docker-compose-dev.yml build
   ```
3. Start the project with
    ```sh
    docker compose -f docker-compose-dev.yml up
    ```
4. Project runs on: http://localhost:8082
5. Visit http://localhost:8082 for API documentation


## Data Loading

##### Quick Load (Docker)

If you're using Docker Compose, use the automated script to load all sample data at once:

```bash
# Load all data with default settings (skip existing farms)
./load_sample_data.sh

# Update existing farms instead of skipping
./load_sample_data.sh --farm-mode update

# Clear all farms and import fresh
./load_sample_data.sh --clear-farms

# View all options
./load_sample_data.sh --help
```

The script will automatically:
- Check Docker is running
- Verify the backend container is up
- Load all sample data in the correct order
- Provide colored progress output
- Show a summary of successes and failures

## Manual Load
#### None Docker users:
Load sample data using individual management commands. Run these from the `backend` directory:


```bash
python manage.py load_locations sample_data/locations.csv # Load Locations (Counties, Subcounties, Wards)

python manage.py load_crops sample_data/crops.csv # Load Crops

python manage.py load_crop_varieties sample_data/crop_variety.csv # Load Crop Varieties

python manage.py load_crop_growth_stages sample_data/crop_growth_stages.csv # Load Crop Growth Stages

python manage.py load_pests sample_data/pest_control.csv # Load Pest Control Data
```

###### Upload Farm Shapefiles:
```bash
# Skip existing farms (default)
python manage.py upload_farms sample_data/farms.zip

# Update existing farms
python manage.py upload_farms sample_data/farms.zip --mode update

# Clear all farms and import fresh
python manage.py upload_farms sample_data/farms.zip --clear
```

#### For Docker users:

```bash
docker exec -it pemost_backend bash -c "cd /pemostbackend && python manage.py load_locations sample_data/locations.csv" # Load locations

docker exec -it pemost_backend bash -c "cd /pemostbackend && python manage.py load_crops sample_data/crops.csv" # Load Crop

docker exec -it pemost_backend bash -c "cd /pemostbackend && python manage.py load_crop_varieties sample_data/crop_variety.csv" #Load Crop Varieties

docker exec -it pemost_backend bash -c "cd /pemostbackend && python manage.py load_crop_growth_stages sample_data/crop_growth_stages.csv" # Load Crop Growth Stages

docker exec -it pemost_backend bash -c "cd /pemostbackend && python manage.py load_pests sample_data/pest_control.csv" # Load Pest Control Data

docker exec -it pemost_backend bash -c "cd /pemostbackend && python manage.py upload_farms sample_data/farms.zip" # Load farm Data
```

## Push Notifications

PeMost supports Firebase Cloud Messaging (FCM) for push notifications. 

#### Quick Setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com)
2. Download service account credentials JSON file for python
3. Copy the downloaded file to backend folder and rename to firebasefile.json
4. Use the API endpoints to register devices and send notifications

```bash
# List registered FCM devices
python manage.py list_devices [--user USER_ID] [--type {ios,android,web}] [--stats]

# Send test push notification
python manage.py test_push user_id [--title TITLE] [--body BODY] [--image IMAGE_URL]

# Test FCM configuration
python manage.py test_fcm [--user-id USER_ID] [--username EMAIL] [--all-devices]
```

#### API Endpoints

- `POST /api/v2/notifications/register/device/` - Register FCM device
- `POST /api/v2/notifications/unregister/device/` - Unregister device
- `GET /api/v2/notifications/devices/` - List user's devices
- `POST /api/v2/notifications/test/push/` - Send test notification (dev only)

## API Documentation

#### Base URL

```
http://127.0.0.1:8000/api/v2/
```

#### Postman Collection

Import `PEMOST.postman_collection.json` into Postman for complete API documentation and testing.

### Key Endpoints

**Authentication**
- `POST /api/v2/auth/login/` - User login
- `POST /api/v2/auth/register/` - User registration
- `POST /api/v2/auth/logout/` - User logout

**Farms**
- `GET /api/v2/app/farms/` - List farms
- `POST /api/v2/app/farms/` - Create farm
- `GET /api/v2/app/farms/` - Get all farms
- `GET /api/v2/app/farms/{id}/` - Get farm details
- `PUT /api/v2/app/farms/{id}/` - Update farm
- `DELETE /api/v2/app/farms/{id}/` - Delete farm
- `POST /api/v2/app/upload/farm/` - Upload farm shapefile

**Plantations**
- `GET /api/v2/app/plantations/` - List plantations
- `POST /api/v2/app/plantations/` - Create plantation

**Locations**
- `GET /api/v2/locations/counties/` - List counties
- `GET /api/v2/locations/subcounties/` - List subcounties
- `GET /api/v2/locations/wards/` - List wards

**Pemost Model posting occurence to the backend**
- `POST /api/v2/pest/control/process/occurence/` - Post occurence


## Firebase Notification API Endpoints Reference

All notification endpoints are prefixed with `/api/v2/notifications/`

### Authentication

All endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer YOUR_JWT_TOKEN
```

### Endpoints

| Endpoint | Method | Description | Auth Required | Production Safe |
|----------|--------|-------------|---------------|-----------------|
| `/register/device/` | POST | Register FCM device for current user | Yes | Yes |
| `/unregister/device/` | POST | Unregister a specific FCM device | Yes | Yes |
| `/devices/` | GET | List all devices for current user | Yes | Yes |
| `/test/push/` | POST | Send test notification to current user | Yes | No (Dev only) |

### Request/Response Examples

### Register Device

**Request:**
```json
POST /api/v2/notifications/register/device/
{
  "registration_id": "fK7xY9...",
  "name": "My Android Phone",
  "device_id": "device-uuid-123",
  "type": "android"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "My Android Phone",
  "registration_id": "fK7xY9...",
  "device_id": "device-uuid-123",
  "type": "android",
  "active": true,
  "date_created": "2025-11-10T10:30:00Z"
}
```

#### List Devices

**Request:**
```
GET /api/v2/notifications/devices/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "My Android Phone",
    "type": "android",
    "active": true,
    "date_created": "2025-11-10T10:30:00Z"
  },
  {
    "id": 2,
    "name": "My Tablet",
    "type": "android",
    "active": true,
    "date_created": "2025-11-09T15:20:00Z"
  }
]
```

#### Send Test Notification (Dev Only)

**Request:**
```json
POST /api/v2/notifications/test/push/
{
  "title": "Test Notification",
  "body": "This is a test message",
  "data": {
    "screen": "home",
    "action": "refresh"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Notification sent successfully",
  "total_devices": 2,
  "successful": 2,
  "failed": 0
}
```

## Troubleshooting

### Database Connection Issues

If you encounter database connection errors:

1. Ensure PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   ```

2. Verify PostGIS extension is installed:
   ```sql
   SELECT PostGIS_version();
   ```

3. Check database credentials in `.env`

### GDAL/OGR Import Errors

If you get GDAL-related errors:

```bash
# Ubuntu/Debian
sudo apt install gdal-bin libgdal-dev

# Set GDAL library path if needed
export GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
```

### Celery Worker Issues

If Celery worker fails to start:

1. Ensure Redis is running:
   ```bash
   redis-cli ping  # Should return PONG
   ```

2. Check Redis connection in settings

3. Purge any celery tasks:
   ```bash
   celery -A project purge
   ```

### Migration Errors

If migrations fail due to missing folders:

```bash
# Ensure each app has a migrations directory
mkdir -p app/migrations locations/migrations crops/migrations pest_control/migrations
touch app/migrations/__init__.py locations/migrations/__init__.py crops/migrations/__init__.py pest_control/migrations/__init__.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Write unit tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

For more information or support, please contact the Pemost development team.