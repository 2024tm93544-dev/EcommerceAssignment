from flask_restx import Namespace, Resource, fields
from app.models import Notification, db
from app.email_service import send_email, get_email_template

ns = Namespace("notifications", description="Notification operations")

# Swagger model for validation and docs
notification_model = ns.model('Notification', {
    'type': fields.String(required=True, description='Notification event type'),
    'data': fields.Raw(required=True, description='Payload data for the notification')
})

@ns.route('/')
class NotificationResource(Resource):
    @ns.expect(notification_model)
    def post(self):
        data = ns.payload

        event_type = data.get("type")
        payload = data.get("data")

        if not event_type or not payload:
            ns.abort(400, "Invalid payload")

        notification = Notification(type=event_type, payload=payload)
        db.session.add(notification)
        db.session.commit()

        try:
            email_body = get_email_template(event_type, payload)
            recipient = payload.get("customer_email", "test@example.com")
            send_email(f"Notification: {event_type}", recipient, email_body)
            notification.status = "SENT"
        except Exception as e:
            notification.status = "FAILED"
            db.session.rollback()
            ns.abort(500, f"Email send failed: {str(e)}")
        finally:
            db.session.commit()

        return {"message": "Notification processed successfully"}, 200
        


