from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import date
from database import SessionLocal, engine
import models, schemas, crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Assignment & Tracking API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- CREATE USER ----------------
@app.post("/users", status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    if user.role not in schemas.ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=409, detail="Email already exists")

    return crud.create_user(db, user)

# ---------------- CREATE TASK (ADMIN ONLY) ----------------
@app.post("/tasks", status_code=201)
def create_task(
    task: schemas.TaskCreate,
    x_user_role: str = Header(...),
    db: Session = Depends(get_db)
):
    if x_user_role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create tasks")

    user = crud.get_user(db, task.assignedTo)
    if not user:
        raise HTTPException(status_code=404, detail="Assigned user not found")

    if task.dueDate <= date.today():
        raise HTTPException(status_code=400, detail="Due date must be in the future")

    return crud.create_task(db, task)

# ---------------- UPDATE TASK STATUS ----------------
@app.patch("/tasks/{task_id}/status")
def update_task_status(
    task_id: int,
    payload: schemas.TaskStatusUpdate,
    db: Session = Depends(get_db)
):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    valid_flow = {
        "pending": "in_progress",
        "in_progress": "completed"
    }

    if payload.status not in schemas.ALLOWED_STATUS:
        raise HTTPException(status_code=400, detail="Invalid status")

    if task.status == payload.status:
        return task

    if valid_flow.get(task.status) != payload.status:
        raise HTTPException(
            status_code=400,
            detail="Invalid status transition"
        )

    task.status = payload.status
    db.commit()
    db.refresh(task)
    return task


@app.get("/tasks")
def fetch_tasks(
    status: str = None,
    assignedTo: int = None,
    dueBefore: date = None,
    db: Session = Depends(get_db)
):
    return crud.get_tasks(db, status, assignedTo, dueBefore)
