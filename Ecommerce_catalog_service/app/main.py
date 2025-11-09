from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from . import crud, schemas

app = FastAPI(title="Catalog Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/v1/products", response_model=schemas.PaginatedProducts)
def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, le=100),
    category: Optional[str] = None,
    price_gt: Optional[float] = None,
    price_lt: Optional[float] = None,
    sort_by_price: Optional[str] = Query(None, regex="^(asc|desc)$"),
    substring: Optional[str] = None
):
    items, total = crud.fetch_products(page, per_page, category, price_gt, price_lt, sort_by_price, substring)
    return {"items": items, "page": page, "per_page": per_page, "total": total}

@app.post("/v1/products", response_model=schemas.ProductOut, status_code=201)
def create_product(product: schemas.ProductCreate):
    product_id = crud.create_product(product)
    # fetch_products returns (rows, total) - pick the first row (the created product)
    rows, total = crud.fetch_products(1, 1, None, None, None, None, product.name)
    if not rows:
        raise HTTPException(status_code=500, detail="Failed to fetch created product")
    prod = rows[0]
    return prod

@app.put("/v1/products/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: str, payload: schemas.ProductUpdate):
    updates = {k: v for k, v in payload.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    updated = crud.update_product(product_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

@app.delete("/v1/products/{product_id}", response_model=schemas.ProductOut)
def delete_product(product_id: str):
    deleted = crud.soft_delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return deleted