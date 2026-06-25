from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_api_key
from src.db import get_db, get_redis
from src.models.api_key import ApiKey
from src.repository.certificate import CertificateRepository
from src.service import trace as trace_service

router = APIRouter()


class TraceIngest(BaseModel):
    agent_id: str
    data: dict[str, Any]


@router.post("", status_code=202)
async def ingest_trace(
    body: TraceIngest,
    api_key: ApiKey = Depends(get_current_api_key),
) -> dict:
    result = await trace_service.ingest(get_redis(), api_key, body.agent_id, body.data)
    return result


@router.get("")
async def list_traces(
    page: int = 1,
    limit: int = 20,
    api_key: ApiKey = Depends(get_current_api_key),
    db: AsyncSession = Depends(get_db),
) -> dict:
    traces, total = await trace_service.list_traces(db, api_key.id, page, limit)
    cert_repo = CertificateRepository(db)
    items = []
    for t in traces:
        cert = await cert_repo.get_by_trace_id(t.id)
        items.append({
            "id": str(t.id),
            "agent_id": t.agent_id,
            "hash": t.hash,
            "payload": t.payload,
            "created_at": t.created_at.isoformat(),
            "certificate_id": str(cert.id) if cert else None,
        })
    return {"items": items, "total": total, "page": page, "limit": limit}
