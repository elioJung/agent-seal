import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.certificate import Certificate


class CertificateRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, *, trace_id: uuid.UUID, hash: str, signature: str) -> Certificate:
        cert = Certificate(id=uuid.uuid4(), trace_id=trace_id, hash=hash, signature=signature)
        self.db.add(cert)
        await self.db.commit()
        await self.db.refresh(cert)
        return cert

    async def get_by_id(self, cert_id: uuid.UUID) -> Certificate | None:
        result = await self.db.execute(select(Certificate).where(Certificate.id == cert_id))
        return result.scalar_one_or_none()

    async def get_by_trace_id(self, trace_id: uuid.UUID) -> Certificate | None:
        result = await self.db.execute(
            select(Certificate).where(Certificate.trace_id == trace_id)
        )
        return result.scalar_one_or_none()
