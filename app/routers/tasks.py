from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from ..auth import require_role
from ..database import get_db
from ..models import Task, Part, User
from ..schemas import TaskCreate, TaskResponse


router = APIRouter(
    prefix="/api/tasks",
    tags=["Tasks"]
)


@router.post(
    "",
    response_model=TaskResponse
)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db)
):

    part = (
        db.query(Part)
        .filter(Part.id == data.part_id)
        .first()
    )

    if not part:
        raise HTTPException(
            status_code=404,
            detail="Part not found"
        )

    worker = (
        db.query(User)
        .filter(
            User.id == data.worker_id,
            User.role == "WORKER",
            User.active == 1
        )
        .first()
    )

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    task = Task(
        part_id=data.part_id,
        worker_id=data.worker_id,
        operation=data.operation,
        quantity=data.quantity,
        deadline=data.deadline,
        priority=data.priority,
        status="NEW"
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@router.get(
    "/my",
    response_model=list[TaskResponse]
)
def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("WORKER")
    )
):

    return (
        db.query(Task)
        .filter(
            Task.worker_id == current_user.id
        )
        .order_by(Task.deadline)
        .all()
    )


@router.put(
    "/{task_id}/start",
    response_model=TaskResponse
)
def start_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    task.status = "IN_PROGRESS"
    task.started_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task


@router.put(
    "/{task_id}/complete",
    response_model=TaskResponse
)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    task.status = "COMPLETED"
    task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task