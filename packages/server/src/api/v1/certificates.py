import uuid

from fastapi import APIRouter, Header

router = APIRouter()


@router.post("/{trace_id}", status_code=201)
async def issue_certificate(
    trace_id: uuid.UUID,
    x_api_key: str = Header(...),
) -> dict:
    # TODO Phase 2: 해시 서명 후 certificates 테이블에 저장
    return {"message": "TODO: implement certificate issuance", "trace_id": str(trace_id)}
