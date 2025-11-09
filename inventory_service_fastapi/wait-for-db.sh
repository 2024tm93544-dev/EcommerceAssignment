#!/bin/sh
set -e

host="inventory-db"
port="5432"

echo "⏳ Waiting for PostgreSQL at $host:$port..."
until nc -z "$host" "$port"; do
  sleep 1
done

echo "✅ Database is up. Starting FastAPI..."
exec "$@"
