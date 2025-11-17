#!/bin/sh
set -e

if [ "$DATABASE" = "postgres" ]; then
    echo "Waiting for PostgreSQL at $POSTGRES_HOST:$DB_PORT..."

    until pg_isready -h "$POSTGRES_HOST" -p "$DB_PORT" -U "$POSTGRES_USER"; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 1
    done

    echo "PostgreSQL is up!"
fi

echo "-------Generate Migration Files------"
python manage.py makemigrations --noinput || exit 1

echo "-------Apply database migrate------"
python manage.py migrate --noinput || exit 1

echo "-------Collect static------"
python manage.py collectstatic --no-input --clear

echo "-------Creating a superuser-------"
python manage.py shell -c "
from django.contrib.auth import get_user_model;
try:
  get_user_model().objects.create_superuser(first_name='Admin',last_name='Strator',email='admin@admin.com',phone_number='+254712345678',password='admin',role='SYSTEM_ADMIN')
except Exception as e:
  print(e)
  "
exec "$@"
