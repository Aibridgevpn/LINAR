from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from ..auth import require_role
from ..database import get_db
from ..models import Order, Product, User
from ..schemas import (
    OrderCreate,
    OrderResponse
)


router = APIRouter(
    prefix="/api/orders",
    tags=["Orders"]
)


@router.post(
    "",
    response_model=OrderResponse
)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("MANAGER")
    )
):

    product = (
        db.query(Product)
        .filter(
            Product.id == data.product_id
        )
        .first()
    )

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    master = (
        db.query(User)
        .filter(
            User.id == data.master_id,
            User.role == "MASTER",
            User.active == 1
        )
        .first()
    )

    if not master:

        raise HTTPException(
            status_code=404,
            detail="Master not found"
        )

    order = Order(
        product_id=data.product_id,
        quantity=data.quantity,

        # Реальный руководитель
        created_by=current_user.id,

        master_id=data.master_id,
        deadline=data.deadline,
        status="ASSIGNED"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return order


@router.get(
    "/master",
    response_model=list[OrderResponse]
)
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("MASTER")
    )
):

    return (
        db.query(Order)
        .filter(
            Order.master_id == current_user.id
        )
        .order_by(
            Order.created_at.desc()
        )
        .all()
    )