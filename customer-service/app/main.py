from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Customer Service")


class CustomerCreate(BaseModel):
    name: str
    email: str


customers = {
    1: {"id": 1, "name": "Alice Tan", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob Lee", "email": "bob@example.com"},
}
next_id = 3


@app.get("/customers")
def get_customers():
    return list(customers.values())


@app.get("/customers/{customer_id}")
def get_customer(customer_id: int):
    customer = customers.get(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.post("/customers", status_code=201)
def register_customer(customer: CustomerCreate):
    global next_id
    new_customer = {"id": next_id, **customer.model_dump()}
    customers[next_id] = new_customer
    next_id += 1
    return new_customer
