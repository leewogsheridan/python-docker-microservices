import os
from contextlib import asynccontextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI(title="Customer Service")


class CustomerCreate(BaseModel):
    name: str
    email: str


customers = {
    1: {"id": 1, "name": "Alice Tan", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob Lee", "email": "bob@example.com"},
}
next_id = 3


# Database connection functions
def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def init_db():
    conn = get_conn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL
                )
            """)

            cur.execute("""
                INSERT INTO customers (name, email)
                SELECT * FROM (VALUES
                    ('Alice Tan', 'alice@example.com'),
                    ('Bob Lee', 'bob@example.com')
                ) AS seed(name, email)
                WHERE NOT EXISTS (SELECT 1 FROM customers)
            """)
    finally:
        conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


# REST API functions


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
