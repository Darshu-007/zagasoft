from sqlalchemy.orm import Session
from models import User, Task
from datetime import date

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_task(db: Session, task):
    db_task = Task(
        title=task.title,
        description=task.description,
        assigned_to=task.assignedTo,
        due_date=task.dueDate
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks(db: Session, status=None, assigned_to=None, due_before=None):
    query = db.query(Task)

    if status:
        query = query.filter(Task.status == status)
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)
    if due_before:
        query = query.filter(Task.due_date < due_before)

    return query.all()
