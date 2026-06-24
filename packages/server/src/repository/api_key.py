import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.api_key import ApiKey
from src.utils.crypto import hash_key


class ApiKeyRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def find_by_raw_key(self, raw_key: str) -> ApiKey | None:
        key_hash = hash_key(raw_key)
        result = await self.db.execute(
            select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: uuid.UUID, key_hash: str, prefix: str) -> ApiKey:
        api_key = ApiKey(id=uuid.uuid4(), user_id=user_id, key_hash=key_hash, prefix=prefix)
        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)
        return api_key
