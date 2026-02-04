import asyncpg
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/todo_db"
)

_db_pool: asyncpg.Pool | None = None


async def get_db() -> asyncpg.Pool:
    """
    Lazy DB initialization + table creation.
    Runs once and guarantees schema exists.
    """
    global _db_pool

    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(DATABASE_URL)

        # 🔥 GUARANTEE TABLE EXISTS
        async with _db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    completed BOOLEAN DEFAULT FALSE
                )
            """)

    return _db_pool