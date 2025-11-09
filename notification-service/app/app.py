from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_restx import Api
import os
from prometheus_flask_exporter import PrometheusMetrics

db = SQLAlchemy()
mail = Mail()
api = Api(
    title="Notification Service",
    version="1.0.0-dev",
    description="Handles notifications for Orders, Payments, and Shipments",
    doc="/v1/"  # Swagger UI will appear here
)

def create_app():
    app = Flask(__name__)
    

    # ✅ Prometheus metrics setup
    metrics = PrometheusMetrics(app, path="/metrics")
    metrics.info('notification_service_info', 'Notification Service Metrics', version='1.0.0')

    # =========================
    # Database Configuration
    # =========================
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@notification-db:5432/notificationdb'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # =========================
    # Mailtrap Configuration
    # =========================
    app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
    app.config['MAIL_PORT'] = 2525
    app.config['MAIL_USERNAME'] = os.getenv('MAILTRAP_USERNAME', 'd302a63a4256cf')
    app.config['MAIL_PASSWORD'] = os.getenv('MAILTRAP_PASSWORD', '17316a9b8b0de8')
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_DEFAULT_SENDER'] = ('Notification Service', 'noreply@notificationservice.com')

    db.init_app(app)
    mail.init_app(app)
    api.init_app(app)


    # Import namespaces (must come after api is initialized)
    from app.routes import ns as notification_ns
    api.add_namespace(notification_ns, path="/v1/notifications")

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)

