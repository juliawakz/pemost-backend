Pemost Backend

PeMost is built on django and postgis database

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
- **Add these variables to .env file lias with env.example**
```
PROJECT_NAME=TerraTask V1.0.0
ALLOWED_HOSTS=*
DEBUG=True/False
SECRET_KEY=your_secret

POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_username
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=your_db_host
DB_PORT=your_db_port
DATABASE=your_db_type

ALLOWED_HOSTS=*

```

- **Migrations**
Make migrations and migrate, incase of any error about abscent folders ensure all modules have a migration folder in migration_files


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
