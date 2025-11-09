# Notification Service

A microservice for automating event-driven notifications for orders, payments, shipments, inventory, and user registration—built with Flask, PostgreSQL, and Mailtrap. Containerized and ready for Docker or Kubernetes.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Directory Structure](#directory-structure)
4. [Dependencies](#dependencies)
5. [Environment Variables](#environment-variables)
6. [Setup & Usage (Docker)](#setup--usage-docker)
7. [Mailtrap Configuration](#mailtrap-configuration)
8. [API Reference](#api-reference)
   - [API Endpoints](#api-endpoints)
9. [Database Schema](#database-schema)
10. [Extending Functionality](#extending-functionality)
11. [Development](#development)
12. [Minikube/Kubernetes Setup](#minikubekubernetes-setup)
13. [Metrics & Observability](#metrics--observability)
14. [Author](#Author)

---

## Project Overview

**Notification Service** is a backend microservice designed to automate event-driven notifications in e-commerce or logistics platforms.

- Handles notifications for orders, payments, shipments, inventory, and user registration.
- Persists every notification event in PostgreSQL for tracking and auditing.
- Generates and delivers templated emails via Mailtrap (safe for dev/testing).
- Offers a RESTful API, documented via Swagger/OpenAPI.
- Deployable with Docker Compose or Kubernetes.

---

## Tech Stack

| Component        | Technology                 | Purpose                                  |
|------------------|---------------------------|------------------------------------------|
| Backend/API      | Flask + Flask-RESTx       | RESTful API server, Swagger docs         |
| ORM/Database     | Flask-SQLAlchemy          | PostgreSQL object-relational mapping     |
| Database         | PostgreSQL                | Persistent notification log              |
| Email            | Flask-Mail + Mailtrap     | SMTP notifications, safe dev inbox       |
| Container/App    | Docker & Compose          | Containerized local deployments          |
| Config           | Python Dotenv             | Environment configuration                |
| Scripting        | Bash                      | Entrypoint and startup scripts           |
| Metrics*/Obs**   | *Prometheus, Grafana*     | *(optional)* Metrics & monitoring        |
| Cloud Platform   | Minikube/Kubernetes       | Cloud-native orchestration               |

---

## Directory Structure
```
notification-service/
│
├── app/                          # Main application package
│   ├── __init__.py               # Marks 'app' as a Python package (can be empty or used for app-wide init logic)
│   ├── app.py                    # Flask app factory, configures extensions and registers namespaces
│   ├── routes.py                 # API routes and endpoint logic for notifications
│   ├── models.py                 # SQLAlchemy models and DB schema definitions
│   ├── email_service.py          # Email templates and sending logic for various event types
│
├── run.py                        # Entrypoint; runs the Flask app using the factory pattern
├── requirements.txt              # Python dependencies and versions
├── Dockerfile                    # Docker image build instructions for the service
├── docker-compose.yaml           # Multi-container orchestration (DB, service)
├── wait-for-db.sh                # Entrypoint script to poll/wait for PostgreSQL to be up before launching the app
├── .gitignore                    # Patterns for files/folders not to be committed to git

```
---

## Dependencies

- Flask
- Flask-RESTx
- Flask-SQLAlchemy
- Flask-Mail
- python-dotenv
- psycopg2-binary

See `requirements.txt` for compatible versions.

---

## Environment Variables

Configure your environment with:

- `DATABASE_URL`: PostgreSQL connection URI
- `MAIL_SERVER`: SMTP host (e.g., `sandbox.smtp.mailtrap.io`)
- `MAIL_PORT`: SMTP port (Mailtrap: `2525`)
- `MAIL_USERNAME`, `MAIL_PASSWORD`: SMTP credentials
- `MAIL_USE_TLS`, `MAIL_USE_SSL`: Security settings

For local dev, use a `.env` file (ignored via `.gitignore`).

---

## Setup & Usage (Docker)

1. **Clone the repository:**
    ```
    git clone <your-repo-url>
    cd notification-service
    ```

2. **Build and start services:**
    ```
    docker-compose up --build
    ```

- Service URL: `http://localhost:5001`
- Swagger docs: `http://localhost:5001/v1/`

---

## Mailtrap Configuration

Mailtrap is a free SMTP service for safe development emails.

1. Register at [mailtrap.io](https://mailtrap.io)
2. Navigate to your inbox and find the SMTP credentials
3. Insert credentials in `.env` or `docker-compose.yaml`:
    ```
    MAIL_SERVER: sandbox.smtp.mailtrap.io
    MAIL_PORT: 2525
    MAIL_USERNAME: your_mailtrap_user
    MAIL_PASSWORD: your_mailtrap_pass
    MAIL_USE_TLS: True
    MAIL_USE_SSL: False
    ```
All notifications will appear in your Mailtrap inbox for review.

---

## API Reference

### API Endpoints

| Method | Endpoint                | Description                  | Payload Required                  | Response                                |
|--------|------------------------ |------------------------------|-----------------------------------|------------------------------------------|
| POST   | `/v1/notifications/`    | Create/send notification     | `type`, `data`                    | `{"message": ...}` or error message      |

**Request Example**  
```
{
"type": "ORDER_CREATED",
"data": {
"order_id": "123",
"order_total": 599,
"customer_email": "user@example.com"
}
}
```

**Supported Notification Types:**
- USER_REGISTERED
- ORDER_CREATED
- PAYMENT_STATUS_CHANGED
- SHIPMENT_DELIVERED
- LOW_INVENTORY_ALERT

**Success:** 200 status, confirmation message  
**Error:** 400 for validation, 500 for internal/send failure

---

## Database Schema

| Field      | Type      | Required | Description                       |
|------------|-----------|----------|-----------------------------------|
| id         | Integer   | Yes      | Primary Key                       |
| type       | String    | Yes      | Notification event type           |
| payload    | JSON      | Yes      | Event data, flexible structure    |
| status     | String    | No       | PENDING/SENT/FAILED (default: PENDING) |
| created_at | DateTime  | No       | UTC timestamp                     |

Database name: `notificationdb` (default, see docker-compose).

---

## Extending Functionality

- **Event types:** Add templates in `email_service.py`
- **API:** Extend `routes.py`
- **Email engine:** Update Flask-Mail config as needed

---

## Development
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# Setup .env & Postgres, then:
python run.py

---

## Minikube/Kubernetes Setup

1. **Install Minikube:**  
   [https://minikube.sigs.k8s.io/docs/start/](https://minikube.sigs.k8s.io/docs/start/)
2. **Start Minikube:**  
   `minikube start`
3. **Configure Docker environment:**  
   `eval $(minikube docker-env)`
4. **Build Docker images:**  
   `docker build -t notification-service:latest .`
5. **Create YAML manifests (deployment/service):**  
   (See example below)
6. **Apply manifests:**  
   `kubectl apply -f notification-service-deployment.yaml`
7. **Expose service:**  
   `minikube service notification-service --url`

Example manifest:
apiVersion: apps/v1
kind: Deployment
metadata:
name: notification-service
spec:
replicas: 1
selector:
matchLabels:
app: notification-service
template:
metadata:
labels:
app: notification-service
spec:
containers:
- name: notification-service
image: notification-service:latest
ports:
- containerPort: 5000

apiVersion: v1
kind: Service
metadata:
name: notification-service
spec:
type: NodePort
selector:
app: notification-service
ports:
- protocol: TCP
port: 5000
targetPort: 5000

---

## Metrics & Observability *(Optional)*

- **Prometheus:** Add `prometheus-flask-exporter` for endpoint metrics.
- **Grafana:** Visualize metrics with dashboards.
- **K8s:** Deploy Prometheus/Grafana in your Minikube cluster.
- **Health endpoints:** Add `/healthz` in your Flask app for readiness/liveness.
- **Logging:** Standard Python logging or integration with ELK.

**Sample metrics integration:**
In app.py
from prometheus_flask_exporter import PrometheusMetrics
metrics = PrometheusMetrics(app)

---

## Author

 UTSAB ROY | 2024tm93539@wilp.bits-pilani.ac.in 

---


