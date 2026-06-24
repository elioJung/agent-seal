import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models.api_key import ApiKey
from src.models.certificate import Certificate
from src.models.trace import Trace
from src.repository.certificate import CertificateRepository
from src.repository.trace import TraceRepository
from src.utils.crypto import sign_hash


async def issue(
    db: AsyncSession,
    api_key: ApiKey,
    trace_id: uuid.UUID,
) -> Certificate:
    trace_repo = TraceRepository(db)
    cert_repo = CertificateRepository(db)

    trace = await trace_repo.get_by_id(trace_id)
    if trace is None:
        raise HTTPException(404, "트레이스를 찾을 수 없습니다")
    if trace.api_key_id != api_key.id:
        raise HTTPException(403, "접근 권한이 없습니다")

    existing = await cert_repo.get_by_trace_id(trace_id)
    if existing:
        raise HTTPException(409, "이미 증명서가 발급된 트레이스입니다")

    return await cert_repo.create(
        trace_id=trace_id,
        hash=trace.hash,
        signature=sign_hash(trace.hash, settings.secret_key),
    )


async def verify(
    db: AsyncSession,
    cert_id: uuid.UUID,
) -> tuple[Certificate, Trace]:
    cert = await CertificateRepository(db).get_by_id(cert_id)
    if cert is None:
        raise HTTPException(404, "증명서를 찾을 수 없습니다")

    trace = await TraceRepository(db).get_by_id(cert.trace_id)
    if trace is None:
        raise HTTPException(500, "연결된 트레이스가 없습니다")

    return cert, trace
