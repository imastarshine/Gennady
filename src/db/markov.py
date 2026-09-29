import time

import aiosqlite


class MarkovDB:
    def __init__(self):
        self.path = "dbs/markov.db"
        self.connection: aiosqlite.Connection | None = None

    async def init(self):
        self.connection = await aiosqlite.connect(self.path)
        await self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pair_one TEXT NOT NULL,
                pair_two TEXT NOT NULL,
                created_at INTEGER
            )
            """
        )
        await self.connection.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_pairs_unique ON pairs (pair_one, pair_two)"
        )
        await self.connection.commit()

    async def can_continue(self, word: str) -> bool:
        cursor = await self.connection.execute(
            "SELECT 1 FROM pairs WHERE pair_one = ? LIMIT 1", (word,)
        )
        row = await cursor.fetchone()
        await cursor.close()
        return row is not None

    async def get_random_word(self, word: str) -> str | None:
        cursor = await self.connection.execute(
            "SELECT pair_two FROM pairs WHERE pair_one = ? ORDER BY RANDOM() LIMIT 1",
            (word,),
        )
        row = await cursor.fetchone()
        await cursor.close()
        return row[0] if row else None

    async def insert_pairs(self, pairs: list[tuple[str, str]]) -> int:
        timestamp = int(time.time())
        cursor = await self.connection.executemany(
            "INSERT OR IGNORE INTO pairs (pair_one, pair_two, created_at) VALUES (?, ?, ?)",
            [(one, two, timestamp) for one, two in pairs],
        )
        await self.connection.commit()
        await cursor.close()
        return cursor.rowcount