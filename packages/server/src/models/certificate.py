import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class Certificate(Base):
    __tablename__ = "certificates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    trace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("traces.id"), nullable=False, unique=True
    )
    hash: Mapped[str] = mapped_column(String(64), nullable=False)   # SHA-256 of payload
    signature: Mapped[str] = mapped_column(String(512), nullable=False)  # HMAC-SHA256
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # no updates — append-only
