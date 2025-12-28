# Remove periodic tasks
if docker exec pemost_backend_prod python manage.py shell -c "from django_celery_beat.models import CrontabSchedule; CrontabSchedule.objects.all().delete()"; then
  echo "Removed cron jobs and periodic tasks successfully"
else
  echo "Backend not running....!"
fi

# Down containers and Remove orphans
while ! docker-compose -f docker-compose-prod.yml down --remove-orphans; do sleep 1; done
docker system prune --all --force

docker volume rm pemost_backend_celery_worker_prod_volume pemost_backend_celery_beat_prod_volume

# Create frontend volume to allow for Angular to build
docker volume ls|grep frontend_volume > /dev/null || docker volume create frontend_volume

# Build and up the containers
docker-compose -f docker-compose-prod.yml build
docker-compose -f docker-compose-prod.yml up -d
docker system prune --all --force
