
# 🛍️ Scalable E-Commerce Microservice System

## 📖 Overview
This project is a **cloud-native, event-driven microservice architecture** built for an e-commerce platform.  
It demonstrates **end-to-end order lifecycle orchestration** — from product catalog browsing to order creation, payment processing, shipment management, inventory sync, and real-time notifications.

The solution is designed for **scalability, resilience, and observability** using modern DevOps and backend engineering practices.

---

## 🧱 System Architecture

```
                         ┌─────────────────────┐
                         │     Frontend UI     │
                         └─────────┬───────────┘
                                   │ REST APIs
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                Backend Microservices                                     │
│                                                                                          │
│  ┌───────────────────┐     ┌───────────────────┐     ┌───────────────────────┐            │
│  │ Catalog Service   │──►──│ Inventory Service │──►──│ Order Service         │───┐        │
│  │ (FastAPI + MySQL) │     │ (FastAPI + PGSQL)│     │ (Django + PGSQL)      │   │        │
│  └───────────────────┘     └───────────────────┘     └───────────────────────┘   │        │
│                                                           │                     │        │
│                                                           ▼                     │        │
│                                            ┌──────────────────────────────┐      │        │
│                                            │ Payment Service (FastAPI)    │      │        │
│                                            │ Simulates charge, refunds    │      │        │
│                                            └──────────────────────────────┘      │        │
│                                                           │                     │        │
│                                                           ▼                     │        │
│                                        ┌────────────────────────────┐            │        │
│                                        │ Shipping Service (Django)  │◄───────────┘        │
│                                        │ Handles tracking & delivery│                     │
│                                        └────────────────────────────┘                     │
│                                                           │                              │
│                                                           ▼                              │
│                                   ┌───────────────────────────────────────┐               │
│                                   │ Notification Service (FastAPI)        │               │
│                                   │ Sends user email alerts via Mailtrap  │               │
│                                   └───────────────────────────────────────┘               │
│                                                                                          │
└──────────────────────────────────────────────────────────────────────────────────────────┘

                          ┌─────────────────────────────────────────┐
                          │   Prometheus + Grafana Monitoring Stack │
                          │   Unified metrics & observability       │
                          └─────────────────────────────────────────┘
```

---

## 🧩 Tech Stack

| Layer | Technology | Purpose |
|-------|-------------|----------|
| **API Frameworks** | Django REST Framework, FastAPI | RESTful microservices |
| **Databases** | PostgreSQL, MySQL | Persistent storage per service |
| **Monitoring** | Prometheus, Grafana | Centralized metrics visualization |
| **Containerization** | Docker, Docker Compose | Portable service orchestration |
| **Notifications** | Mailtrap (SMTP sandbox) | Email delivery simulation |
| **Language** | Python 3.12+ | Backend microservices |

---

## 🔄 Inter-Service Flow

1. **Catalog Service** → Provides product catalog  
2. **Inventory Service** → Manages stock levels  
3. **Order Service** → Orchestrates full lifecycle (inventory, payment, shipping, notifications)  
4. **Payment Service** → Processes payments  
5. **Shipping Service** → Tracks delivery and updates order status  
6. **Notification Service** → Sends emails for order, payment, and delivery events  

---

## 🧰 Setup Instructions

### 1️⃣ Clone Repository
```bash
git clone https://github.com/<your-repo>/scalable-ecommerce.git
cd scalable-ecommerce
```

### 2️⃣ Build Environment
```bash
docker compose build
```

### 3️⃣ Start All Services
```bash
docker compose up -d
```

### 4️⃣ Verify
Visit:
- Catalog → http://localhost:8000/docs  
- Inventory → http://localhost:8002/docs  
- Orders → http://localhost:8003/orders-doc  
- Shipping → http://localhost:8004/ship-doc  
- Notifications → http://localhost:8005/docs  
- Prometheus → http://localhost:9090  
- Grafana → http://localhost:3000  

---

## 📦 Seed Data
Each service auto-loads sample data via `seed_db.py` or Docker entrypoints.

---

## 💌 Notification Templates

| Event Type | Description |
|-------------|-------------|
| ORDER_CREATED | Sent when order is created |
| PAYMENT_STATUS_CHANGED | Payment status change |
| SHIPMENT_DELIVERED | Sent upon successful delivery |
| LOW_INVENTORY_ALERT | Optional inventory alert |

---

## 📈 Monitoring
All services expose `/metrics` endpoints for Prometheus.

Prometheus scrapes metrics:
```yaml
scrape_configs:
  - job_name: 'catalog-service'
    static_configs: [{ targets: ['catalog-service:8000'] }]
  - job_name: 'order-service'
    static_configs: [{ targets: ['order-service:8001'] }]
```

Grafana connects to Prometheus at `http://prometheus:9090`.

---

## 🚀 Future Enhancements
- API Gateway (Kong / Traefik)  
- Async events (Kafka / RabbitMQ)  
- Distributed tracing (Jaeger)  
- Role-based Auth  
- Kubernetes deployment  

---

## 🧑‍💻 Author
**Utsab Roy**  

