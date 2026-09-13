from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from ..auth import require_role
from ..database import get_db
from ..models import Product, User
from ..schemas import (
    ProductCreate,
    ProductResponse
)


router = APIRouter(
    prefix="/api/products",
    tags=["Products"]
)


@router.get(
    "",
    response_model=list[ProductResponse]
)
def get_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            "MANAGER",
            "MASTER"
        )
    )
):

    return (
        db.query(Product)
        .order_by(Product.id)
        .all()
    )


@router.post(
    "",
    response_model=ProductResponse
)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("MANAGER")
    )
):

    existing = (
        db.query(Product)
        .filter(
            Product.article == data.article
        )
        .first()
    )

    if existing:

        raise HTTPException(
            status_code=409,
            detail="Article already exists"
        )

    product = Product(
        name=data.name,
        article=data.article,
        description=data.description
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product