import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.service import certificate as cert_service

router = APIRouter()


@router.get("/{cert_id}")
async def verify_certificate(
    cert_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    cert, trace = await cert_service.verify(db, cert_id)
    return {
        "valid": True,
        "certificate": {
            "id": str(cert.id),
            "trace_id": str(cert.trace_id),
            "hash": cert.hash,
            "signature": cert.signature,
            "issued_at": cert.issued_at.isoformat(),
        },
        "trace": {
            "id": str(trace.id),
            "agent_id": trace.agent_id,
            "hash": trace.hash,
            "created_at": trace.created_at.isoformat(),
        },
    }
