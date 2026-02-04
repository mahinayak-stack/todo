from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import asyncpg

app = FastAPI(title="Simple Todo App")

DATABASE_URL = "postgresql://todo_user:todo_pass@localhost:5432/todo_db"

db = None

@app.on_event("startup")
async def startup():
    global db
    db = await asyncpg.create_pool(DATABASE_URL)

@app.on_event("shutdown")
async def shutdown():
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
@app.post("/tasks", response_model=TaskOut)
async def create_task(task: TaskIn):
    row = await db.fetchrow(
        "INSERT INTO tasks (title, description) VALUES ($1,$2) RETURNING *",
        task.title,
        task.description,
    )
    return dict(row)


@app.get("/tasks", response_model=List[TaskOut])
async def get_tasks():
    rows = await db.fetch("SELECT * FROM tasks ORDER BY id")
    return [dict(row) for row in rows]


@app.get("/tasks/{id}", response_model=TaskOut)
async def get_task(id: int):
    task = await db.fetchrow("SELECT * FROM tasks WHERE id=$1", id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(task)


@app.put("/tasks/{id}", response_model=TaskOut)
async def update_task(id: int, task: TaskUpdate):
    updated = await db.fetchrow(
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
    result = await db.execute("DELETE FROM tasks WHERE id=$1", id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}