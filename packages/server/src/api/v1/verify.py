import uuid

from fastapi import APIRouter

router = APIRouter()


@router.get("/{cert_id}")
async def verify_certificate(cert_id: uuid.UUID) -> dict:
    # TODO Phase 2: 인증 없이 공개 검증
    return {"message": "TODO: implement verification", "cert_id": str(cert_id)}
