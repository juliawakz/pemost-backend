** Local Development
- Set up database POSTGRES 
- Install GDAL in the system 
- Clone the project 
- Cd to backend 
- Copy env.example to .env and edit the variables 
- Create venv and activate 
- Install requirements using pip install -r requirements/dev.txt 
- Make migartions and migrate, incase of any error about abscent folders ensure all modules have a migration folder in migration_files. 
- Run application python manage.py runserver