# backend/Dockerfile
ARG FLASK_PORT

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE ${FLASK_PORT}
CMD ["python3", "main.py"]