import os
from contextlib import asynccontextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DATABASE_URL = os.getenv("DATABASE_URL")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Customer Service", lifespan=lifespan)


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


# REST API functions
@app.get("/customers")
def get_customers():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email FROM customers ORDER BY id")
            return cur.fetchall()
    finally:
        conn.close()


@app.get("/customers/{customer_id}")
def get_customer(customer_id: int):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, email FROM customers WHERE id = %s", (customer_id,)
            )
            customer = cur.fetchone()
    finally:
        conn.close()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.post("/customers", status_code=201)
def register_customer(customer: CustomerCreate):
    conn = get_conn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO customers (name, email) VALUES (%s, %s) RETURNING id, name, email",
                (customer.name, customer.email),
            )
            return cur.fetchone()
    finally:
        conn.close()
