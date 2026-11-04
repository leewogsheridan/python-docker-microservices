from fastapi import FastAPI, HTTPException

app = FastAPI(title="Product Service")

# Sample product database

products = [

{

    "id": 1,

    "name": "Laptop",

    "price": 1200,

    "stock": 10

},

{

    "id": 2,

    "name": "Keyboard",

    "price": 50,

    "stock": 25

},

{

    "id": 3,

    "name": "Mouse",

    "price": 30,

    "stock": 40

},

{

    "id": 4,

    "name": "Monitor",

    "price": 300,

    "stock": 15

}

]

@app.get("/")
def home():
    return {"message": "Welcome toProduct Service"}

@app.get("/health")
def health():
    return { 
            "status": "healthy",
            "service": "product-service"
    }

@app.get("/products")
def get_products():
    return products

@app.get("/products/{product_id}")
def get_product(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(status_code=404, detail="Product not found")