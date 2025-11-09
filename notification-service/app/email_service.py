from flask_mail import Message
from app.app import mail
from flask import render_template_string

TEMPLATE_BUILDERS = {
    "USER_REGISTERED": lambda d: f"Welcome {d.get('name', 'User')}! Your account has been successfully created.",
    "ORDER_CREATED": lambda d: f"Your order #{d.get('order_id')} has been created with total ₹{d.get('order_total')}.",
    "PAYMENT_STATUS_CHANGED": lambda d: f"Payment {d.get('reference', 'N/A')} for order #{d.get('order_id')} is {d.get('status', 'N/A')}.",
    "SHIPMENT_DELIVERED": lambda d: f"Your order #{d.get('order_id')} has been delivered via {d.get('carrier', 'N/A')}.",
    "LOW_INVENTORY_ALERT": lambda d: f"Inventory low for SKU {d.get('sku', 'N/A')} at warehouse {d.get('warehouse', 'N/A')} (on hand: {d.get('on_hand', 'N/A')}).",
}

def get_email_template(event_type, data):
    return TEMPLATE_BUILDERS.get(event_type, lambda d: "Notification event received.")(data)


def send_email(subject, recipient, body):
    msg = Message(subject=subject, recipients=[recipient], body=body)
    mail.send(msg)

def get_email_template(event_type, data):
    return TEMPLATE_BUILDERS.get(event_type, lambda d: "Notification event received.")(data)

