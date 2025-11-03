#!/bin/sh
# Ensure a runtime fallback if NEXT_PUBLIC_API_URL was not provided when starting the container
: "${NEXT_PUBLIC_API_URL:=http://localhost:5000}"
export NEXT_PUBLIC_API_URL

# Exec the Next standalone server (server.js expects env vars available at require time)
exec node server.js
