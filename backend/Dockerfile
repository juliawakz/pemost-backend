FROM python:3.12-slim

# Python env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install GDAL + system deps
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        gdal-bin \
        libgdal-dev \
        build-essential \
        postgresql-client \
        python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Working directories
RUN mkdir -p /pemostbackend/static \
    /pemostbackend/media \
    /pemostbackend/database/backups

WORKDIR /pemostbackend

# Copy dependencies
COPY requirements/prod.txt /pemostbackend/requirements.txt

# Install Python deps
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /pemostbackend/requirements.txt

# Copy project files
COPY . .

# Fix entrypoint permissions
RUN sed -i 's/\r$//g' /pemostbackend/entrypoint.sh && \
    chmod +x /pemostbackend/entrypoint.sh

ENTRYPOINT ["/pemostbackend/entrypoint.sh"]
