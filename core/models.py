from pydantic import BaseModel

class TodoIn(BaseModel):
    title: str
    description: str | None = None

class TodoOut(TodoIn):
    id: int
    completed: bool