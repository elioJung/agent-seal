from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.models.api_key import ApiKey
from src.repository.api_key import ApiKeyRepository


async def get_current_api_key(
    x_api_key: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> ApiKey:
    repo = ApiKeyRepository(db)
    api_key = await repo.find_by_raw_key(x_api_key)
    if api_key is None:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")
    return api_key
