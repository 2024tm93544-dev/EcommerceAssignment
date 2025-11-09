#!/bin/bash
set -e

echo "Starting initialization with following parameters:"
echo "MYSQL_HOST: $MYSQL_HOST"
echo "MYSQL_USER: $MYSQL_USER"
echo "MYSQL_DB: $MYSQL_DB"
echo "Current working directory: $(pwd)"

echo "Checking if CSV file exists..."
if [ ! -f "/app/data/eci_products.csv" ]; then
    echo "Error: CSV file not found at /app/data/eci_products.csv"
    echo "Contents of /app/data:"
    ls -la /app/data
    exit 1
fi

# Wait for database to be ready
echo "Waiting for database initialization..."
max_retries=30
counter=0

while [ $counter -lt $max_retries ]; do
    if mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1" 2>/dev/null; then
        echo "Successfully connected to MySQL!"
        
        # Verify database exists
        echo "Verifying database $MYSQL_DB exists..."
        if ! mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "USE $MYSQL_DB" 2>/dev/null; then
            echo "Database $MYSQL_DB does not exist. Creating it..."
            mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $MYSQL_DB;"
        fi
        
        # Check if table exists and has data
        echo "Checking if table exists and has data..."
        COUNT=$(mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" $MYSQL_DB -N -e "SELECT COUNT(*) FROM catalogue;" 2>/dev/null || echo "0")
        
        if [ "$COUNT" = "0" ]; then
            echo "Table is empty. Loading data..."
            echo "Running: python csv_loader.py --host $MYSQL_HOST --user $MYSQL_USER --db $MYSQL_DB --csv /app/data/eci_products.csv"
            if python csv_loader.py --host "$MYSQL_HOST" --user "$MYSQL_USER" --password "$MYSQL_PASSWORD" --db "$MYSQL_DB" --csv /app/data/eci_products.csv; then
                echo "✅ Data loading completed successfully"
                
                # Verify data was loaded
                NEW_COUNT=$(mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" $MYSQL_DB -N -e "SELECT COUNT(*) FROM catalogue;")
                echo "Rows in catalogue table: $NEW_COUNT"
                exit 0
            else
                echo "❌ Error: Failed to load CSV data"
                exit 1
            fi
        else
            echo "Table already has $COUNT rows. Skipping data load."
            exit 0
        fi
    fi
    
    echo "Attempt $counter: MySQL connection failed, retrying in 2 seconds..."
    sleep 2
    counter=$((counter + 1))
done

echo "Error: Failed to connect to MySQL after $max_retries attempts"
exit 1