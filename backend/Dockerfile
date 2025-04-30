FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Additional PostgreSQL dependencies 
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "600", "--workers", "2", "--threads", "2", "--worker-class", "gthread", "--access-logfile", "-", "--log-level", "info", "--capture-output", "app.app:app"]