#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! curl http://$POSTGRES_HOST:$DB_PORT/ 2>&1 | grep '52'
    do
      sleep 1
    done

    echo "PostgreSQL started"
fi

echo "-------Generate Migartion Files------"
python manage.py makemigrations --noinput || exit 1

echo "-------Apply database migrate------"
python manage.py migrate --noinput || exit 1

echo "-------Collect static------"
python manage.py collectstatic --no-input --clear

echo "-------Creating a superuser-------"
python manage.py shell -c "
from django.contrib.auth import get_user_model;
try:
  get_user_model().objects.create_superuser(first_name='Julia',last_name='Wakaba',email='juliawakaba53@gmail.com',phone_number='+254791049498',password='test1234',role='SYSTEM_ADMIN')
except Exception as e:
  print(e)
  "
exec "$@"
