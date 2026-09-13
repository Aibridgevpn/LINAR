from fastapi import FastAPI

from .database import Base, engine

from .routers import (
    auth,
    products,
    orders,
    parts,
    tasks,
    users
)


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="LINAR Production API",
    description="Система управления производством",
    version="1.0.0"
)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(parts.router)
app.include_router(tasks.router)


@app.get("/")
def root():

    return {
        "message": "LINAR Production API",
        "status": "running"
    }