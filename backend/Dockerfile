FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

COPY . .

EXPOSE 5000
USER pwuser
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "1200", "--workers", "2", "--threads", "2", "--worker-class", "gthread", "--access-logfile", "-", "--log-level", "info", "--capture-output", "app.app:app"]
