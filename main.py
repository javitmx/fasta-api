from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración de la base de datos SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definición del modelo de Producto
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    quantity = Column(Integer)
    description = Column(String)
    price = Column(Float)

# Crea la base de datos y las tablas
Base.metadata.create_all(bind=engine)

# FastAPI
app = FastAPI()

# Modelos de datos Pydantic para las operaciones CRUD
class ProductCreate(BaseModel):
    title: str
    quantity: int
    description: str
    price: float

class ProductUpdate(BaseModel):
    title: str = None
    quantity: int = None
    description: str = None
    price: float = None

class ProductResponse(ProductCreate):
    id: int

# Rutas de la API
@app.post("/products/", response_model=ProductResponse)
def create_product(product: ProductCreate):
    db = SessionLocal()
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=List[ProductResponse])
def read_products(skip: int = 0, limit: int = 10):
    db = SessionLocal()
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@app.get("/products/{product_id}", response_model=ProductResponse)
def read_product(product_id: int):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate):
    db = SessionLocal()
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict().items():
        if value is not None:
            setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    db = SessionLocal()
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}

# Crear 10 productos de prueba
def create_initial_products():
    db = SessionLocal()
    initial_products = [
        Product(title=f"Product {i}", quantity=10, description=f"Description {i}", price=10.0 * i)
        for i in range(1, 11)
    ]
    db.add_all(initial_products)
    db.commit()

create_initial_products()
