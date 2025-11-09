FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["./wait-for-db.sh", "notification-db", "python", "run.py"]

