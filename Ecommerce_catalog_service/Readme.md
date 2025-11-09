# Product Catalog Service

A FastAPI-based RESTful service for managing product catalogs with MySQL backend.

## Features

- CRUD operations for products
- Pagination support
- Filtering by category, price range, and name
- Sorting by price
- Soft delete functionality
- Connection pooling for database operations
- CSV data import utility

## Project Structure

```
catalog/
├─ app/
│  ├─ __init__.py
│  ├─ main.py         # FastAPI application and route definitions
│  ├─ config.py       # Configuration settings
│  ├─ db.py          # Database connection management
│  ├─ models.py      # Database models
│  ├─ schemas.py     # Pydantic models for request/response
│  ├─ crud.py        # Database operations
│  └─ utils.py       # Utility functions
├─ requirements.txt   # Project dependencies
├─ Dockerfile        # Container configuration
├─ ddl_mysql.sql    # Database schema
├─ load_csv_to_mysql.py  # Data import utility
└─ README.md
```

## API Endpoints

- `GET /v1/products` - List products with filtering and pagination
  - Query Parameters:
    - `page`: Page number (default: 1)
    - `per_page`: Items per page (default: 10, max: 100)
    - `category`: Filter by category
    - `price_gt`: Filter by price greater than
    - `price_lt`: Filter by price less than
    - `sort_by_price`: Sort by price (asc/desc)
    - `substring`: Search in product names

- `POST /v1/products` - Create a new product
- `PUT /v1/products/{sku}` - Update a product by SKU
- `DELETE /v1/products/{sku}` - Soft delete a product by SKU

## Setup

1. Set up a Python virtual environment:
```bash
# Create a new virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On Unix or MacOS:
source .venv/bin/activate
```

2. Install dependencies in the virtual environment:
```bash
# Make sure your virtual environment is activated (you should see (.venv) in your terminal)
pip install -r requirements.txt
```

2. Set up the database:
```bash
mysql -u root -p < ddl.sql
```
OR 
manually run the ddl.sql contents from your mysql workbench/cmd

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the `MYSQL_PASSWORD` in `.env` with your database password
   - Optionally override other database settings in `.env`

4. Load sample data (optional):
```bash
python load_csv_to_mysql.py --password your_mysql_password
```

## Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Running with Docker Compose

This project supports running the API, MySQL database, and data loader using Docker Compose. This is the recommended way to get started for local development or testing.

### Ports
Mysql Server -- 3307
Catalog API service -- 8000

### Quick Start

1. Build and start all services (API, MySQL, and data loader):

```bash
docker-compose up --build
```

- The MySQL database will be initialized with the schema from `ddl.sql`.
- The data loader service will automatically import products from `eci_products.csv` into the database using `csv_loader.py`.
- The FastAPI server will be available at [http://localhost:8000](http://localhost:8000)

2. To stop and remove all containers, networks, and volumes:

```bash
docker-compose down -v
```

### How Data Loading Works
- The data loader service waits for the MySQL database to be healthy, then runs:
  ```bash
  python csv_loader.py --host db --user root --password <your_password> --db ecommerce --csv /app/data/eci_products.csv
  ```
- There is no need for a separate shell script; the loader runs directly as a service.
- If you want to reload data, you can remove the database volume and restart the services.

### Customizing Database Credentials
- By default, the MySQL root password is set via the `MYSQL_PASSWORD` environment variable (see `docker-compose.yml`).
- You can override this by creating a `.env` file or setting environment variables before running Docker Compose.

## Virtual Environment Management

### Activating the Environment
```bash
# On Windows:
.venv\Scripts\activate
# On Unix or MacOS:
source .venv/bin/activate
```

### Deactivating the Environment
When you're done working on the project, you can deactivate the virtual environment:
```bash
deactivate
```

### Best Practices
- Always activate the virtual environment before working on the project
- Install all packages while the virtual environment is activated
- Keep `requirements.txt` up to date by running `pip freeze > requirements.txt` when you add new dependencies
- Don't commit the `.venv` directory to version control (it's included in .gitignore)

## Dependencies

- FastAPI
- Uvicorn
- MySQL Connector Python
- Pydantic
- Pydantic-Settings

## Database Schema

```sql
CREATE TABLE catalogue (
  product_id INT PRIMARY KEY AUTO_INCREMENT,
  sku VARCHAR(64) NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  category VARCHAR(100),
  price DECIMAL(10,2),
  is_active BOOLEAN DEFAULT TRUE
);
```
