from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from ..auth import (
    get_current_user,
    hash_password,
    require_role
)

from ..database import get_db
from ..models import User
from ..schemas import (
    UserCreate,
    UserResponse,
    UserUpdate
)


router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


VALID_ROLES = {
    "MANAGER",
    "MASTER",
    "WORKER"
}


# =========================================================
# GET CURRENT USER
# =========================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):

    return current_user


# =========================================================
# GET ALL USERS
# =========================================================

@router.get(
    "",
    response_model=list[UserResponse]
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("MANAGER")
    )
):

    return (
        db.query(User)
        .order_by(User.name)
        .all()
    )


# =========================================================
# GET MASTERS
# =========================================================

@router.get(
    "/masters",
    response_model=list[UserResponse]
)
def get_masters(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("MANAGER", "MASTER")
    )
):

    return (
        db.query(User)
        .filter(
            User.role == "MASTER",
            User.active == 1
        )
        .order_by(User.name)
        .all()
    )


# =========================================================
# GET WORKERS
# =========================================================

@router.get(
    "/workers",
    response_model=list[UserResponse]
)
def get_workers(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("MANAGER", "MASTER")
    )
):

    return (
        db.query(User)
        .filter(
            User.role == "WORKER",
            User.active == 1
        )
        .order_by(User.name)
        .all()
    )


# =========================================================
# GET USER BY ID
# =========================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("MANAGER")
    )
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# =========================================================
# CREATE USER
# =========================================================

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("MANAGER")
    )
):

    if data.role not in VALID_ROLES:

        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    existing_user = (
        db.query(User)
        .filter(User.login == data.login)
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=409,
            detail="Login already exists"
        )

    user = User(
        name=data.name,
        login=data.login,
        password_hash=hash_password(
            data.password
        ),
        role=data.role,
        active=1
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# =========================================================
# UPDATE USER
# =========================================================

@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("MANAGER")
    )
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if data.login is not None:

        existing_user = (
            db.query(User)
            .filter(
                User.login == data.login,
                User.id != user_id
            )
            .first()
        )

        if existing_user:

            raise HTTPException(
                status_code=409,
                detail="Login already exists"
            )

        user.login = data.login

    if data.name is not None:
        user.name = data.name

    if data.role is not None:

        if data.role not in VALID_ROLES:

            raise HTTPException(
                status_code=400,
                detail="Invalid role"
            )

        user.role = data.role

    if data.active is not None:
        user.active = data.active

    db.commit()
    db.refresh(user)

    return user


# =========================================================
# DELETE / DISABLE USER
# =========================================================

@router.delete(
    "/{user_id}"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("MANAGER")
    )
):

    if user_id == current_user.id:

        raise HTTPException(
            status_code=400,
            detail="You cannot delete yourself"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Не удаляем физически,
    # чтобы сохранить историю производства.
    user.active = 0

    db.commit()

    return {
        "message": "User disabled"
    }