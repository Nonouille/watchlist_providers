# backend/Dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
# Added --access-logfile, --log-level, and --capture-output flags for logging
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "--log-level", "info", "--capture-output", "app.app:app"]