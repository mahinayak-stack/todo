from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import asyncpg

app = FastAPI(title="Simple Todo App")

DATABASE_URL = "postgresql://todo_user:todo_pass@localhost:5432/todo_db"

db: asyncpg.Pool | None = None


def get_db():
    """
    Always use this function to access the database.
    In tests, `db` can be replaced with a mock.
    """
    if db is None:
        raise RuntimeError("Database not initialized")
    return db


@app.on_event("startup")
async def startup():
    global db
    db = await asyncpg.create_pool(DATABASE_URL)


@app.on_event("shutdown")
async def shutdown():
    if db:
        await db.close()


class TaskIn(BaseModel):
    title: str
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskOut(TaskIn):
    id: int
    completed: bool


# --------------------
# ROUTES
# --------------------
@app.post("/tasks", response_model=TaskOut)
async def create_task(task: TaskIn):
    database = get_db()
    row = await database.fetchrow(
        """
        INSERT INTO tasks (title, description)
        VALUES ($1, $2)
        RETURNING *
        """,
        task.title,
        task.description,
    )
    return dict(row)


@app.get("/tasks", response_model=List[TaskOut])
async def get_tasks():
    database = get_db()
    rows = await database.fetch("SELECT * FROM tasks ORDER BY id")
    return [dict(row) for row in rows]


@app.get("/tasks/{id}", response_model=TaskOut)
async def get_task(id: int):
    database = get_db()
    task = await database.fetchrow("SELECT * FROM tasks WHERE id=$1", id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(task)


@app.put("/tasks/{id}", response_model=TaskOut)
async def update_task(id: int, task: TaskUpdate):
    database = get_db()
    updated = await database.fetchrow(
        """
        UPDATE tasks
        SET title = COALESCE($1, title),
            description = COALESCE($2, description),
            completed = COALESCE($3, completed)
        WHERE id = $4
        RETURNING *
        """,
        task.title,
        task.description,
        task.completed,
        id,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(updated)


@app.delete("/tasks/{id}")
async def delete_task(id: int):
    database = get_db()
    result = await database.execute("DELETE FROM tasks WHERE id=$1", id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}