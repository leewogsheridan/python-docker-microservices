import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Order Service")

# Product Service address
PRODUCT_SERVICE_URL = "http://localhost:8001"

# Sample order storage
orders = []


# Order request model
class OrderRequest(BaseModel):
    product_id: int
    quantity: int


@app.get("/")
def home():
    return {"message": "Welcome to Order Service"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "order-service"}


@app.post("/orders")
def create_order(order: OrderRequest):
    # Contact Product Service
    try:
        response = requests.get(
            f"{PRODUCT_SERVICE_URL}/products/{order.product_id}", timeout=5
        )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Product not found")
        response.raise_for_status()
        product = response.json()
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Product Service is unavailable")

    # Check stock
    if order.quantity <= 0:
        raise HTTPException(
            status_code=400, detail="Quantity must be greater than zero"
        )

    if order.quantity > product["stock"]:
        raise HTTPException(status_code=400, detail="Insufficient product stock")

    # Calculate order amount
    total_price = product["price"] * order.quantity

    # Create order
    new_order = {
        "order_id": len(orders) + 1,
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": order.quantity,
        "unit_price": product["price"],
        "total_price": total_price,
    }
    orders.append(new_order)

    return {"message": "Order created successfully", "order": new_order}


@app.get("/orders")
def get_orders():
    return orders
