Pemost Backend

PeMost is built on DRF and postgis database

## Quick Start
- **Clone repository**
- **Create python3 environment**
```
python3 -m venv pemost_env
```
- **Change to the working directory**
```
cd pemostv2_backend
```
- **Install the requirements**
```
pip3 install requirements/dev.txt
```
- **Create an environment variable file**
```
touch .env
```
- **Here are some of the variables. To add all variables to .env file lias with pemostv2-backend/backend/env.example file**
```
PROJECT_NAME=project name
ALLOWED_HOSTS=*
DEBUG=True/False
SECRET_KEY=your_secret

POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_username
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=your_db_host
DB_PORT=your_db_port
DATABASE=your_db_type

```

- **Migrations**
Make migrations and migrate, incase of any error about abscent folders ensure all modules have a migration folder in migration_files

- **load location data**
```
python manage.py load_locations pemostv2-backend/backend/sample_data/locationscsv
```

- **Create a superuser Account and follow the prompts**
```
python manage.py createsuperuser

```
- **Use the credentials created above to log in to the admin Interface through the link below**
```
http://127.0.0.1:8000/admin
```
- **Development Server**
```
python manage.py runserver
```
- **Run redis worker**
```
celery -A project worker -l info
```
- **Collection**
```
PEMOST.postman_collection.json can be found on the project folder
```
