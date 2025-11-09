from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from .database import Base, engine, SessionLocal
from .routers import inventory
from .seed_data import seed_inventory_data
from . import crud
import time

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Inventory Microservice", version="1.4")
app.include_router(inventory.router)

def run_reaper_job():
    db = SessionLocal()
    crud.release_expired_reservations(db)
    db.close()

@app.on_event("startup")
def startup_event():
    # seed database
    seed_inventory_data()

    # allow scheduler to run every minute
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_reaper_job, "interval", minutes=1)
    scheduler.start()
