import asyncpg
import os
from fastapi import FastAPI

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/todo_db"
)


async def init_db(app: FastAPI):
    """
    Create pool bound to the current event loop.
    """
    app.state.db_pool = await asyncpg.create_pool(DATABASE_URL)

    async with app.state.db_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT FALSE
            )
        """)


async def close_db(app: FastAPI):
    await app.state.db_pool.close()


async def get_db(app: FastAPI) -> asyncpg.Pool:
    return app.state.db_pool