import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_api_key
from src.db import get_db
from src.models.api_key import ApiKey
from src.service import certificate as cert_service

router = APIRouter()


@router.post("/{trace_id}", status_code=201)
async def issue_certificate(
    trace_id: uuid.UUID,
    api_key: ApiKey = Depends(get_current_api_key),
    db: AsyncSession = Depends(get_db),
) -> dict:
    cert = await cert_service.issue(db, api_key, trace_id)
    return {
        "id": str(cert.id),
        "trace_id": str(cert.trace_id),
        "hash": cert.hash,
        "signature": cert.signature,
        "issued_at": cert.issued_at.isoformat(),
        "verify_url": f"/verify/{cert.id}",
    }
