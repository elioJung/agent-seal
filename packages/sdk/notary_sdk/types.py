from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TracePayload:
    agent_id: str
    data: dict[str, Any]
    timestamp: str = field(default_factory=_now_iso)


@dataclass
class NotaryEvent:
    trace_id: str
    agent_id: str
    status: str  # "sent" | "failed"
    timestamp: str = field(default_factory=_now_iso)
