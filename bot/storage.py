"""Chat context storage using SQLite."""

import json
import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "chat_history.db"


async def init_db():
    """Initialize the database and create tables if needed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_id ON messages(user_id)
        """)
        await db.commit()


async def add_message(user_id: int, role: str, content: str):
    """Add a message to the conversation history."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content),
        )
        await db.commit()


async def get_context(user_id: int, max_messages: int = 20) -> list[dict]:
    """Get recent conversation context for a user."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT role, content FROM messages
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, max_messages),
        )
        rows = await cursor.fetchall()

    # Reverse to get chronological order
    return [{"role": row[0], "content": row[1]} for row in reversed(rows)]


async def clear_context(user_id: int):
    """Clear conversation history for a user."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
        await db.commit()


async def get_stats() -> dict:
    """Get usage statistics."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(DISTINCT user_id) FROM messages")
        total_users = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM messages")
        total_messages = (await cursor.fetchone())[0]

    return {"total_users": total_users, "total_messages": total_messages}
