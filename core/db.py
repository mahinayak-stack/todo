import asyncpg
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/todo_db"
)

db: asyncpg.Pool | None = None


async def connect_db():
    global db
    db = await asyncpg.create_pool(DATABASE_URL)


async def disconnect_db():
    global db
    if db:
        await db.close()