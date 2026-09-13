from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Part, Order
from ..schemas import PartCreate, PartResponse


router = APIRouter(
    prefix="/api/parts",
    tags=["Parts"]
)


@router.post(
    "",
    response_model=PartResponse
)
def create_part(
    data: PartCreate,
    db: Session = Depends(get_db)
):

    order = (
        db.query(Order)
        .filter(Order.id == data.order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    part = Part(
        order_id=data.order_id,
        name=data.name,
        article=data.article,
        quantity=data.quantity,
        material=data.material,
        description=data.description,
        status="NEW"
    )

    db.add(part)
    db.commit()
    db.refresh(part)

    return part


@router.get(
    "/order/{order_id}",
    response_model=list[PartResponse]
)
def get_order_parts(
    order_id: int,
    db: Session = Depends(get_db)
):

    return (
        db.query(Part)
        .filter(Part.order_id == order_id)
        .order_by(Part.id)
        .all()
    )