from app.database import SessionLocal
from app.models import User
from app.auth import hash_password


db = SessionLocal()

try:

    manager = User(
        name="Главный руководитель",
        login="admin",
        password_hash=hash_password("admin123"),
        role="MANAGER"
    )

    db.add(manager)

    master = User(
        name="Иванов Иван Иванович",
        login="master1",
        password_hash=hash_password("master123"),
        role="MASTER"
    )

    db.add(master)

    worker = User(
        name="Петров Петр Петрович",
        login="worker1",
        password_hash=hash_password("worker123"),
        role="WORKER"
    )

    db.add(worker)

    db.commit()

    print("Users created")

finally:
    db.close()