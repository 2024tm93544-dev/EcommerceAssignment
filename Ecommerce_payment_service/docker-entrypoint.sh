#!/bin/sh

# Exit on error
set -e

# Wait for MySQL to be ready
echo "⏳ Waiting for MySQL..."
until nc -z ${MYSQL_HOST:-db} 3306; do
  sleep 1
done
echo "✅ MySQL is ready!"

# Check if 'payments' table already exists to avoid duplicate seeding
echo "🔍 Checking if payments table already exists..."
TABLE_EXISTS=$(mysql --ssl=0 -h ${MYSQL_HOST:-db} -u ${MYSQL_USER:-root} -p${MYSQL_PASSWORD:-rootpass} -D ${MYSQL_DB:-ecommerce} -sse "SHOW TABLES LIKE 'payments';")

if [ -z "$TABLE_EXISTS" ]; then
  echo "⚙️ Creating and seeding 'payments' table from eci_payments.csv..."
  python /app/csv_loader.py \
    --host ${MYSQL_HOST:-db} \
    --user ${MYSQL_USER:-root} \
    --password ${MYSQL_PASSWORD:-rootpass} \
    --db ${MYSQL_DB:-ecommerce} \
    --csv /app/eci_payments.csv || echo "⚠️ Seeding skipped or failed."
else
  echo "✅ 'payments' table already exists. Skipping seed."
fi

# Start the Payment API service
echo "🚀 Starting Payment Service..."
exec "$@"

