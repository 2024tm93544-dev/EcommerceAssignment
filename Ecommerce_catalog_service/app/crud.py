from .db import get_connection

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

    query = "SELECT * FROM catalogue WHERE 1=1"
    count_query = "SELECT COUNT(*) as total FROM catalogue WHERE 1=1"
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
    cursor.execute(
        "INSERT INTO catalogue (sku, name, category, price, is_active) VALUES (%s,%s,%s,%s,%s)",
        (product.sku, product.name, product.category, product.price, product.is_active)
    )
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
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
    query = f"UPDATE catalogue SET {', '.join(fields)} WHERE product_id=%s"
    cursor.execute(query, tuple(values))
    conn.commit()

    # Get the product post-update
    cursor.execute("SELECT * FROM catalogue WHERE product_id=%s", (product_id,))
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
    cursor.execute("SELECT * FROM catalogue WHERE product_id=%s", (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return 0

    # Perform soft delete
    cursor.execute("UPDATE catalogue SET is_active=FALSE WHERE product_id=%s", (product_id,))
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
