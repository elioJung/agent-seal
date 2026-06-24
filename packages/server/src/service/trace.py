import json
import uuid
from typing import Any

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.api_key import ApiKey
from src.models.trace import Trace
from src.repository.trace import TraceRepository
from src.utils.crypto import hash_payload

STREAM = "notary:traces"


async def ingest(
    redis: aioredis.Redis,
    api_key: ApiKey,
    agent_id: str,
    data: dict[str, Any],
) -> dict[str, str]:
    trace_id = uuid.uuid4()
    payload_hash = hash_payload(agent_id, data)

    await redis.xadd(
        STREAM,
        {
            "trace_id": str(trace_id),
            "api_key_id": str(api_key.id),
            "agent_id": agent_id,
            "payload": json.dumps(data, default=str),
            "hash": payload_hash,
        },
    )

    return {"trace_id": str(trace_id), "hash": payload_hash}


async def list_traces(
    db: AsyncSession,
    api_key_id: uuid.UUID,
    page: int,
    limit: int,
) -> tuple[list[Trace], int]:
    return await TraceRepository(db).list_by_api_key(api_key_id, page, limit)
