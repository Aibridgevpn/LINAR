
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ============================================================
# AUTH
# ============================================================

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ============================================================
# USERS
# ============================================================

class UserResponse(BaseModel):
    id: int
    name: str
    login: str
    role: str
    active: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class UserCreate(BaseModel):
    name: str
    login: str
    password: str
    role: str


class UserUpdate(BaseModel):
    name: str | None = None
    login: str | None = None
    role: str | None = None
    active: int | None = None


# ============================================================
# PRODUCTS
# ============================================================

class ProductCreate(BaseModel):
    name: str
    article: str
    description: str | None = None


class ProductResponse(ProductCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# ORDERS
# ============================================================

class OrderCreate(BaseModel):
    product_id: int
    quantity: int
    master_id: int
    deadline: datetime | None = None


class OrderResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    created_by: int
    master_id: int
    deadline: datetime | None
    status: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# PARTS
# ============================================================

class PartCreate(BaseModel):
    order_id: int
    name: str
    article: str | None = None
    quantity: int
    material: str | None = None
    description: str | None = None


class PartResponse(PartCreate):
    id: int
    status: str

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# TASKS
# ============================================================

class TaskCreate(BaseModel):
    part_id: int
    worker_id: int
    operation: str
    quantity: int
    deadline: datetime | None = None
    priority: str = "NORMAL"


class TaskResponse(TaskCreate):
    id: int
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    comment: str | None

    model_config = ConfigDict(
        from_attributes=True
    )

