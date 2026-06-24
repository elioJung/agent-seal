"""Langfuse 트레이스를 NotaryTracePayload 형식으로 변환하는 어댑터."""
import logging
from typing import Any

logger = logging.getLogger(__name__)


class LangfuseAdapter:
    """Langfuse trace 객체를 Notary data dict으로 변환한다."""

    def convert(self, langfuse_trace: Any) -> dict[str, Any]:
        return {
            "agent_id": getattr(langfuse_trace, "name", "unknown"),
            "data": {
                "trace_id": getattr(langfuse_trace, "id", None),
                "input": getattr(langfuse_trace, "input", None),
                "output": getattr(langfuse_trace, "output", None),
                "metadata": getattr(langfuse_trace, "metadata", {}),
            },
        }
