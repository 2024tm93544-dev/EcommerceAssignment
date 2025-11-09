from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from . import crud, schemas
from datetime import datetime
from fastapi.responses import Response

app = FastAPI(title="Payments Service", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.post("/v1/payments/charge", status_code=201)
def charge_payment(payload: schemas.PaymentCharge):
    """Create a payment record probabilistically and return reference + status message."""
    row = crud.create_payment_probabilistic(payload.order_id, payload.amount)
    if not row:
        raise HTTPException(status_code=500, detail="Failed to create payment")

    ref = row.get("reference")
    status_val = row.get("status")
    # convert DB boolean status to human readable
    status = "SUCCESS" if status_val == 1 else "FAILED"
    msg = "Payment succeeded" if status_val == 1 else "Payment failed"
    return {"reference": ref, "status": status, "message": msg}


@app.post("/v1/payments/{payment_id}/refund", response_model=schemas.RefundResponse)
def refund_payment(payment_id: int):
    """Idempotent refund endpoint.

    If payment was SUCCESS, mark REFUNDED and return amount/method. If already REFUNDED, return same.
    If payment failed or not found, raise 400/404 accordingly.
    """
    payment = crud.fetch_payment_by_id(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    result = crud.refund_payment(payment_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    if result is False:
        raise HTTPException(status_code=400, detail="Payment had failed; cannot issue refund")

    return {"payment_id": result["payment_id"], "amount": float(result["amount"]), "method": result["method"], "message": f"Amount {result['amount']} refunded to {result['method']}"}


@app.get("/v1/payments", response_model=schemas.PaginatedPayments)
def list_payments(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, le=200),
    order_id: Optional[int] = None,
    method: Optional[str] = None,
    status: Optional[str] = None,
    amount_gt: Optional[float] = None,
    amount_lt: Optional[float] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by_created: Optional[str] = Query("desc", regex="^(asc|desc)$")
):
    # pass through filters to crud
    items, total = crud.fetch_payments(page=page, per_page=per_page, order_id=order_id, method=method, status=status, amount_gt=amount_gt, amount_lt=amount_lt, start_date=start_date, end_date=end_date, sort_by_created=sort_by_created)
    return {"items": items, "page": page, "per_page": per_page, "total": total}


@app.get("/metrics")
def metrics():
    """
    Prometheus-style metrics endpoint.
    Returns:
        - payments_failed_total
        - payments_refunded_total
        - payments_by_method{method="UPI"} etc.
    """
    # 1️⃣ Fetch payments data for metrics using appropriate filters
    failed_payments, failed_count = crud.fetch_payments(page=1, per_page=1_000_000, status="FAILED")
    refunded_payments, refunded_count = crud.fetch_payments(page=1, per_page=1_000_000, refunded="True")
    upi_payments, upi_count = crud.fetch_payments(page=1, per_page=1_000_000, method="UPI")
    card_payments, card_count = crud.fetch_payments(page=1, per_page=1_000_000, method="CARD")
    cod_payments, cod_count = crud.fetch_payments(page=1, per_page=1_000_000, method="COD")

    # 2️⃣ Build Prometheus-style metrics output
    lines = []
    lines.append("# HELP payments_failed_total Total number of failed payments")
    lines.append("# TYPE payments_failed_total counter")
    lines.append(f"payments_failed_total {failed_count}")

    lines.append("# HELP payments_refunded_total Total number of refunded payments")
    lines.append("# TYPE payments_refunded_total counter")
    lines.append(f"payments_refunded_total {refunded_count}")

    lines.append("# HELP payments_by_method_total Total number of payments per payment method")
    lines.append("# TYPE payments_by_method_total counter")
    lines.append(f'payments_by_method_total{{method="UPI"}} {upi_count}')
    lines.append(f'payments_by_method_total{{method="CARD"}} {card_count}')
    lines.append(f'payments_by_method_total{{method="COD"}} {cod_count}')

    # 3️⃣ Return as text/plain
    output = "\n".join(lines) + "\n"
    return Response(content=output, media_type="text/plain")
