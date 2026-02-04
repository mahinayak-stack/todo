from fastapi import FastAPI, HTTPException
from core.db import connect_db, disconnect_db, db
from core.models import TodoIn, TodoOut
from typing import List

app = FastAPI(title="Todo API")

# ---------------- LIFECYCLE ----------------

@app.on_event("startup")
async def startup():
    await connect_db()

    # create table if not exists
    await db.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT FALSE
        )
    """)

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

# ---------------- ROUTES ----------------

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/todos", response_model=List[TodoOut])
async def get_todos():
    rows = await db.fetch("SELECT * FROM todos ORDER BY id")
    return [dict(r) for r in rows]

@app.post("/todos", response_model=TodoOut)
async def create_todo(todo: TodoIn):
    row = await db.fetchrow(
        """
        INSERT INTO todos (title, description)
        VALUES ($1, $2)
        RETURNING *
        """,
        todo.title,
        todo.description,
    )
    return dict(row)

@app.put("/todos/{todo_id}", response_model=TodoOut)
async def update_todo(todo_id: int, todo: TodoIn):
    row = await db.fetchrow(
        """
        UPDATE todos
        SET title=$1, description=$2
        WHERE id=$3
        RETURNING *
        """,
        todo.title,
        todo.description,
        todo_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Todo not found")
    return dict(row)

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    result = await db.execute(
        "DELETE FROM todos WHERE id=$1",
        todo_id,
    )
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"deleted": True}