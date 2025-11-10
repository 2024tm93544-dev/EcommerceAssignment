from .db import get_connection
import requests
import os

# Inventory Service URL inside Docker network
INVENTORY_SYNC_URL = os.getenv("INVENTORY_SYNC_URL", "http://inventory-service:8000/v1/inventory/sync")
def sync_with_inventory(product):
    """Sync product info to the Inventory Service."""
    try:
        payload = {
            "product_id": product["product_id"],
        }
        res = requests.post(INVENTORY_SYNC_URL, json=payload, timeout=5)

        if res.status_code in (200, 201):
            print(f"✅ Synced with Inventory: Product_id={product['product_id']}")
        else:
            print(f"⚠️ Failed to sync inventory ({res.status_code}): {res.text}")

    except Exception as e:
        print(f"🚫 Inventory sync error: {e}")

def fetch_products(
    page=1,
    per_page=10,
    category=None,
    price_gt=None,
    price_lt=None,
    sort_by_price=None,
    substring=None
):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM products WHERE 1=1"
    count_query = "SELECT COUNT(*) as total FROM products WHERE 1=1"
    params = []
    count_params = []

    # ---- Filters ----
    if category:
        query += " AND category = %s"
        count_query += " AND category = %s"
        params.append(category)
        count_params.append(category)

    if price_gt is not None:
        query += " AND price >= %s"
        count_query += " AND price >= %s"
        params.append(price_gt)
        count_params.append(price_gt)

    if price_lt is not None:
        query += " AND price <= %s"
        count_query += " AND price <= %s"
        params.append(price_lt)
        count_params.append(price_lt)

    if substring:
        query += " AND name LIKE %s"
        count_query += " AND name LIKE %s"
        pattern = f"%{substring}%"
        params.append(pattern)
        count_params.append(pattern)

    # Always only show active products
    query += " AND is_active = TRUE"
    count_query += " AND is_active = TRUE"

    # ---- Sorting ----
    if sort_by_price in ('asc', 'desc'):
        query += f" ORDER BY price {sort_by_price.upper()}"
    else:
        query += " ORDER BY product_id ASC"

    # ---- Pagination ----
    query += " LIMIT %s OFFSET %s"
    params.extend([per_page, (page - 1) * per_page])

    # ---- Execute ----
    cursor.execute(query, params)
    rows = cursor.fetchall()

    cursor.execute(count_query, count_params)
    total = cursor.fetchone()["total"]

    conn.close()
    return rows, total

def create_product(product):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM products WHERE sku = %s", (product.sku,))
    existing = cursor.fetchone()

    if existing:
        # Either update it or raise a meaningful message
        raise ValueError(f"Product with SKU {product.sku} already exists (id={existing['product_id']})")

    
    cursor.execute(
        "INSERT INTO products (sku, name, category, price, is_active) VALUES (%s,%s,%s,%s,%s)",
        (product.sku, product.name, product.category, product.price, product.is_active)
    )
    conn.commit()
    product_id = cursor.lastrowid
    
    cursor.execute("SELECT * FROM products WHERE product_id=%s", (product_id,))
    new_product = cursor.fetchone()
    conn.close()
    
    if new_product:
        sync_with_inventory(new_product)

    return product_id

def update_product(product_id, product_data):
    conn = get_connection()
    # Use dictionary cursor so fetched rows are dicts (not tuples)
    cursor = conn.cursor(dictionary=True)
    fields = []
    values = []
    for k, v in product_data.items():
        fields.append(f"{k}=%s")
        values.append(v)
    values.append(product_id)
    query = f"UPDATE products SET {', '.join(fields)} WHERE product_id=%s"
    cursor.execute(query, tuple(values))
    conn.commit()

    # Get the product post-update
    cursor.execute("SELECT * FROM products WHERE product_id=%s", (product_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return 0

    # Normalize types for JSON/Pydantic
    try:
        if row.get('price') is not None:
            row['price'] = float(row['price'])
    except Exception:
        pass

    # Ensure is_active is a bool
    try:
        row['is_active'] = bool(row.get('is_active'))
    except Exception:
        pass

    conn.close()
    if row:
        sync_with_inventory(row)
    return row

def soft_delete_product(product_id):
    """Soft-delete a product by product_id and return the product dict.

    Returns:
        dict: the product row (with `is_active` set to False) on success
        0: if no product was found to delete
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Get the product first
    cursor.execute("SELECT * FROM products WHERE product_id=%s", (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return 0

    # Perform soft delete
    cursor.execute("UPDATE products SET is_active=FALSE WHERE product_id=%s", (product_id,))
    conn.commit()

    # Normalize types for JSON/Pydantic
    try:
        # price might be Decimal
        if 'price' in row and row['price'] is not None:
            row['price'] = float(row['price'])
    except Exception:
        pass
    # is_active stored as 1/0 or True/False; set to False because we soft-deleted
    row['is_active'] = False

    conn.close()
    return row
