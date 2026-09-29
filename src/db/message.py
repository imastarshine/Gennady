import aiosqlite
from telebot.types import Message


CONTENT_FIELDS = ("text", "video", "video_message", "picture", "voice_message", "sticker", "animation")


class MessageDB:
    def __init__(self):
        self.path = "dbs/messages.db"
        self.connection: aiosqlite.Connection | None = None

    async def init(self):
        self.connection = await aiosqlite.connect(self.path)
        await self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                text TEXT,
                video TEXT,
                video_message TEXT,
                picture TEXT,
                voice_message TEXT,
                sticker TEXT,
                animation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS content_flags (
                content_type TEXT PRIMARY KEY,
                available INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        for content_type in CONTENT_FIELDS:
            await self.connection.execute(
                "INSERT OR IGNORE INTO content_flags (content_type, available) VALUES (?, 0)",
                (content_type,),
            )
        for content_type in CONTENT_FIELDS:
            await self._check_content(content_type)
        await self.connection.commit()

    async def append(
        self,
        message: Message,
        text: str | None = None,
        video: str | None = None,
        video_message: str | None = None,
        picture: str | None = None,
        voice_message: str | None = None,
        sticker: str | None = None,
        animation: str | None = None,
    ):
        values = dict(zip(CONTENT_FIELDS, (text, video, video_message, picture, voice_message, sticker, animation)))
        if not any(values.values()):
            return None

        for content_type in CONTENT_FIELDS:
            if values[content_type] is not None:
                break
        else:
            return None

        await self.connection.execute(
            """
            INSERT INTO messages (user_id, chat_id, text, video, video_message, picture, voice_message, sticker, animation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (message.from_user.id, message.chat.id, *values.values()),
        )
        await self._mark_content(content_type, True)
        await self.connection.commit()
        return None

    async def get_random_content(self, content_type: str) -> str | None:
        cursor = await self.connection.execute(
            f"SELECT {content_type} FROM messages WHERE {content_type} IS NOT NULL ORDER BY RANDOM() LIMIT 1"
        )
        row = await cursor.fetchone()
        await cursor.close()
        return row[0] if row else None

    async def get_available_content_types(self) -> list[str]:
        cursor = await self.connection.execute(
            "SELECT content_type FROM content_flags WHERE available = 1"
        )
        rows = await cursor.fetchall()
        await cursor.close()
        return [row[0] for row in rows]

    async def _mark_content(self, content_type: str, has_content: bool):
        await self.connection.execute(
            "UPDATE content_flags SET available = ? WHERE content_type = ?",
            (1 if has_content else 0, content_type),
        )

    async def _check_content(self, content_type: str):
        cursor = await self.connection.execute(
            f"SELECT id FROM messages WHERE {content_type} IS NOT NULL LIMIT 1"
        )
        row = await cursor.fetchone()
        await cursor.close()
        await self._mark_content(content_type, row is not None)