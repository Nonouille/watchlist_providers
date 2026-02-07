# Use the official PostgreSQL image (smaller variant)
FROM postgres:15-alpine

# Set environment variables
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_DB
ARG POSTGRES_PORT

ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_DB=${POSTGRES_DB}

# Create a directory for initialization scripts
RUN mkdir -p /docker-entrypoint-initdb.d

# Copy initialization scripts
COPY ./init.sql /docker-entrypoint-initdb.d/

# Make sure scripts are executable
RUN chmod +x /docker-entrypoint-initdb.d/*.sql 2>/dev/null || true

# Expose PostgreSQL port
EXPOSE ${POSTGRES_PORT}

# Create a volume for persistent data storage
VOLUME ["/var/lib/postgresql/data"]

# Start PostgreSQL
CMD ["postgres"]
