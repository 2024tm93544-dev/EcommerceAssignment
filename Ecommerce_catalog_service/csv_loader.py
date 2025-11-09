#!/usr/bin/env python3
"""
Simple CSV → MySQL loader for product catalog.
"""

import csv
import mysql.connector
import argparse

def connect_db(host, user, password, database):
    """Establish a connection to MySQL."""
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

def create_table_if_not_exists(conn):
    """Create the catalogue table if it doesn't exist, using CSV's schema (no AUTO_INCREMENT)."""
    cursor = conn.cursor()
    ddl = """
    CREATE TABLE IF NOT EXISTS catalogue (
        product_id INT PRIMARY KEY,
        sku VARCHAR(64) NOT NULL UNIQUE,
        name VARCHAR(255) NOT NULL,
        category VARCHAR(100),
        price DECIMAL(10,2),
        is_active BOOLEAN DEFAULT TRUE
    );
    """
    cursor.execute(ddl)
    conn.commit()
    cursor.close()
    print("✅ Ensured table 'catalogue' exists.")

def load_csv(csv_path, conn):
    """Read the CSV and insert/update rows."""
    cursor = conn.cursor()
    with open(csv_path, newline='') as csvfile:
        # Try to detect delimiter automatically, but assume tab if not comma-separated
        sample = csvfile.read(1024)
        csvfile.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters="\t,")
        reader = csv.DictReader(csvfile, dialect=dialect)

        for row in reader:

            sql = """
                INSERT INTO catalogue (product_id, sku, name, category, price, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    sku=VALUES(sku),
                    name=VALUES(name),
                    category=VALUES(category),
                    price=VALUES(price),
                    is_active=VALUES(is_active);
            """
            vals = (
                int(row['product_id']),
                row['sku'],
                row['name'],
                row['category'],
                float(row['price']),
                bool(row['is_active'])
            )
            cursor.execute(sql, vals)

    conn.commit()
    cursor.close()
    print("✅ CSV data successfully loaded into 'catalogue' table.")

def main():
    parser = argparse.ArgumentParser(description="Load CSV into MySQL 'catalogue' table")
    parser.add_argument("--csv", default="eci_products.csv", help="Path to CSV file")
    parser.add_argument("--host", default="127.0.0.1", help="MySQL host")
    parser.add_argument("--user", default="root", help="MySQL username")
    parser.add_argument("--password", required=True, help="MySQL password")
    parser.add_argument("--db", default="ecommerce", help="Target database name")
    args = parser.parse_args()

    conn = connect_db(args.host, args.user, args.password, args.db)
    create_table_if_not_exists(conn)
    load_csv(args.csv, conn)
    conn.close()

if __name__ == "__main__":
    main()
