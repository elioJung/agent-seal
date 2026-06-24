from typing import Any

from fastapi import APIRouter, Header
from pydantic import BaseModel

router = APIRouter()


class TraceIngest(BaseModel):
    agent_id: str
    data: dict[str, Any]


@router.post("", status_code=202)
async def ingest_trace(
    body: TraceIngest,
    x_api_key: str = Header(...),
) -> dict:
    # TODO Phase 2: API Key 검증 → Redis Streams에 발행
    return {"message": "TODO: implement trace ingestion", "agent_id": body.agent_id}


@router.get("")
async def list_traces(
    x_api_key: str = Header(...),
    page: int = 1,
    limit: int = 20,
) -> dict:
    # TODO Phase 2: API Key 기반 트레이스 조회
    return {"items": [], "total": 0, "page": page, "limit": limit}
