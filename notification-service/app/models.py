from app.app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    payload = db.Column(JSON, nullable=False)
    status = db.Column(db.String(20), default="PENDING")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

