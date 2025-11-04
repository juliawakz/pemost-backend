FROM python:3.8.3
FROM osgeo/gdal:ubuntu-small-3.6.3

# Python Domain
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


RUN apt-get update -y \
    && apt-get install build-essential binutils -y

RUN apt-get install python3-pip -y

# Pemost Files location
RUN mkdir -p /pemostbackend
RUN mkdir -p /pemostbackend/static
RUN mkdir -p /pemostbackend/media
RUN mkdir -p /pemostbackend/database/backups


# Set working directory
WORKDIR /pemostbackend

# Copy depency file
COPY requirements/prod.txt /pemostbackend/requirements.txt
#COPY database/db.sql /docker-entrypoint-initdb.d/

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements/prod.txt /requirements.txt
RUN pip install --no-cache-dir -r /pemostbackend/requirements.txt

# Clean up
RUN apt-get purge -y binutils

RUN rm -rf /var/lib/apt/lists/*
# Copy all files to workingdir
COPY . .

# Print working directory
RUN echo "$PWD"
RUN echo $(ls -a /pemostbackend)

# Give docker write and read access
RUN sed -i 's/\r$//g' /pemostbackend/entrypoint.sh
RUN chmod +x /pemostbackend/entrypoint.sh


ENTRYPOINT ["/pemostbackend/entrypoint.sh"]
