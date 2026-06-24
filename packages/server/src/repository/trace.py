import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.trace import Trace


class TraceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        *,
        trace_id: uuid.UUID,
        api_key_id: uuid.UUID,
        agent_id: str,
        payload: dict,
        hash: str,
    ) -> Trace:
        trace = Trace(
            id=trace_id,
            api_key_id=api_key_id,
            agent_id=agent_id,
            payload=payload,
            hash=hash,
        )
        self.db.add(trace)
        await self.db.commit()
        await self.db.refresh(trace)
        return trace

    async def get_by_id(self, trace_id: uuid.UUID) -> Trace | None:
        result = await self.db.execute(select(Trace).where(Trace.id == trace_id))
        return result.scalar_one_or_none()

    async def list_by_api_key(
        self, api_key_id: uuid.UUID, page: int, limit: int
    ) -> tuple[list[Trace], int]:
        total = await self.db.scalar(
            select(func.count()).select_from(Trace).where(Trace.api_key_id == api_key_id)
        )
        result = await self.db.execute(
            select(Trace)
            .where(Trace.api_key_id == api_key_id)
            .order_by(Trace.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        return list(result.scalars().all()), total or 0
