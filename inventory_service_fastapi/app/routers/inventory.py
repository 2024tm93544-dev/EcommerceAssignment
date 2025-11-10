from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import crud, schemas

router = APIRouter(prefix="/v1/inventory", tags=["Inventory"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/onhand", response_model=list[schemas.InventoryResponse])
def get_on_hand(product_id: int, db: Session = Depends(get_db)):
    return crud.get_inventory(db, product_id)

@router.post("/reserve", response_model=schemas.InventoryResponse)
def reserve(req: schemas.OperationRequest, db: Session = Depends(get_db)):
    return crud.reserve_stock(db, req.product_id, req.quantity)

@router.post("/release", response_model=schemas.InventoryResponse)
def release(req: schemas.OperationRequest, db: Session = Depends(get_db)):
    return crud.release_stock(db, req.product_id, req.quantity)

@router.post("/ship", response_model=schemas.InventoryResponse)
def ship(req: schemas.OperationRequest, db: Session = Depends(get_db)):
    return crud.ship_stock(db, req.product_id, req.quantity)

@router.post("/reaper")
def manual_reaper(db: Session = Depends(get_db)):
    released = crud.release_expired_reservations(db)
    return {"released_reservations": released}

@router.post("/sync", response_model=schemas.InventoryResponse)
def sync_product(product: schemas.InventorySync, db: Session = Depends(get_db)):
    """
    Sync product data from Catalog service.
    - If product_id exists → update price
    - If not → create new inventory entry
    """
    existing = crud.get_inventory_by_product_id(db, product.product_id)
    if existing:
        updated = crud.update_inventory_by_product_id(db,product.product_id, product)
        return updated
    else:
        new_item = crud.create_inventory_from_sync(db, product)
        return new_item

