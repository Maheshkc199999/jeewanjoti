FROM python:3.11-slim

WORKDIR /app

# ✅ Install system dependencies required for mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    libssl-dev \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ✅ Copy and install requirements
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ✅ Copy your Django project files
COPY . .

# Change this if you're using gunicorn or celery or anything else
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]