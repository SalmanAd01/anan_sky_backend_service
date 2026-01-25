from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URI, DATABASE_NAME


class MongoDB:
    _client: AsyncIOMotorClient | None = None

    @classmethod
    def client(cls) -> AsyncIOMotorClient:
        if cls._client is None:
            cls._client = AsyncIOMotorClient(MONGODB_URI)
        return cls._client

    @classmethod
    def db(cls):
        return cls.client()[DATABASE_NAME]


def get_db():
    return MongoDB.db()
