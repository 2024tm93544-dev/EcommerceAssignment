import pandas as pd
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Inventory

def seed_inventory_data():
    db: Session = SessionLocal()
    if db.query(Inventory).count() > 0:
        db.close()
        return

    df = pd.read_csv("seed/inventory.csv")
    for _, row in df.iterrows():
        inv = Inventory(
            product_id=row["product_id"],
            warehouse=row["warehouse"],
            on_hand=row["on_hand"],
            reserved=row.get("reserved", 0)
        )
        db.add(inv)
    db.commit()
    db.close()
    print("✅ Inventory seeded successfully")
