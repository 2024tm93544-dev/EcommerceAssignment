#!/bin/bash
set -e

echo "Waiting for MySQL to be ready..."
until nc -z ${MYSQL_HOST:-catalog-db} 3306; do
  sleep 2
done
echo "✅ MySQL is ready."

# Check if the products table exists and has data
echo "Checking Catalog DB for existing data..."
TABLE_COUNT=$(mysql -h ${MYSQL_HOST:-catalog-db} -uroot -p${MYSQL_PASSWORD:-rootpass} -se "USE ${MYSQL_DB:-ecommerce}; SHOW TABLES LIKE 'products';" | wc -l || echo 0)
ROW_COUNT=$(mysql -h ${MYSQL_HOST:-catalog-db} -uroot -p${MYSQL_PASSWORD:-rootpass} -se "USE ${MYSQL_DB:-ecommerce}; SELECT COUNT(*) FROM products;" 2>/dev/null || echo 0)

if [ "$TABLE_COUNT" -eq 0 ]; then
  echo "⚙️ Creating products table and seeding data..."
  python /app/csv_loader.py --host ${MYSQL_HOST:-catalog-db} --user root --password ${MYSQL_PASSWORD:-rootpass} --db ${MYSQL_DB:-ecommerce} --csv /app/data/eci_products.csv
elif [ "$ROW_COUNT" -eq 0 ]; then
  echo "⚙️ Seeding products data (empty table)..."
  python /app/csv_loader.py --host ${MYSQL_HOST:-catalog-db} --user root --password ${MYSQL_PASSWORD:-rootpass} --db ${MYSQL_DB:-ecommerce} --csv /app/data/eci_products.csv
else
  echo "✅ Products already seeded ($ROW_COUNT rows found). Skipping seeding."
fi

# Finally, run the main app
echo "🚀 Starting Catalog Service..."
exec "$@"

