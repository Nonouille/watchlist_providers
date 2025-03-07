# Use the official PostgreSQL image
FROM postgres:15

# Set environment variables
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=root
ENV POSTGRES_DB=checklist

# Create a directory for initialization scripts
RUN mkdir -p /docker-entrypoint-initdb.d

# Copy initialization scripts
COPY ./create_db.sql /docker-entrypoint-initdb.d/

# Make sure scripts are executable
RUN chmod +x /docker-entrypoint-initdb.d/*.sql 2>/dev/null || true

# Expose PostgreSQL port
EXPOSE 5432

# Create a volume for persistent data storage
VOLUME ["/var/lib/postgresql/data"]

# Start PostgreSQL
CMD ["postgres"]