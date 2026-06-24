"""Langfuse 트레이스를 Notary data dict으로 변환하는 어댑터."""
import logging
from typing import Any

logger = logging.getLogger(__name__)


class LangfuseAdapter:
    """Langfuse trace 객체를 Notary TracePayload data로 변환한다.

    Usage (Langfuse SDK 직접 사용 시):
        adapter = LangfuseAdapter()
        langfuse = Langfuse(...)
        trace = langfuse.get_trace(trace_id)
        payload = adapter.convert(trace)
        await notary_client.send_trace(TracePayload(**payload))

    Usage (LangChain/LangGraph 콜백 사용 시):
        handler = CallbackHandler(...)
        result = app.invoke(input, config={"callbacks": [handler]})
        trace_id = handler.get_trace_id()
        trace = langfuse.get_trace(trace_id)
        payload = adapter.convert(trace)
    """

    def convert(self, langfuse_trace: Any) -> dict[str, Any]:
        observations = getattr(langfuse_trace, "observations", None) or []

        # 첫 번째 Generation에서 모델·사용량 정보를 추출한다
        generations = [
            o for o in observations
            if getattr(o, "type", "").upper() == "GENERATION"
        ]
        primary_gen = generations[0] if generations else None

        usage = self._extract_usage(primary_gen)
        latency_ms = self._extract_latency(langfuse_trace)
        obs_summary = self._summarize_observations(observations)

        data: dict[str, Any] = {
            "langfuse_trace_id": getattr(langfuse_trace, "id", None),
            "task_name": getattr(langfuse_trace, "name", None),
            "input": getattr(langfuse_trace, "input", None),
            "output": getattr(langfuse_trace, "output", None),
            "latency_ms": latency_ms,
            "tags": getattr(langfuse_trace, "tags", []) or [],
            "session_id": getattr(langfuse_trace, "session_id", None),
            "user_id": getattr(langfuse_trace, "user_id", None),
            "metadata": getattr(langfuse_trace, "metadata", None) or {},
        }

        if primary_gen:
            data["model"] = getattr(primary_gen, "model", None)

        if usage:
            data["usage"] = usage

        if obs_summary:
            data["observations"] = obs_summary

        return {
            "agent_id": getattr(langfuse_trace, "name", "unknown-agent"),
            "data": {k: v for k, v in data.items() if v is not None},
        }

    def _extract_usage(self, generation: Any) -> dict[str, Any] | None:
        if generation is None:
            return None
        usage = getattr(generation, "usage", None)
        if usage is None:
            return None
        result: dict[str, Any] = {}
        for field, key in [
            ("input", "input_tokens"),
            ("output", "output_tokens"),
            ("total", "total_tokens"),
            ("total_cost", "total_cost"),
        ]:
            val = getattr(usage, field, None)
            if val is not None:
                result[key] = val
        return result or None

    def _extract_latency(self, trace: Any) -> int | None:
        start = getattr(trace, "timestamp", None)
        end = getattr(trace, "end_time", None) or getattr(trace, "updatedAt", None)
        if start and end:
            try:
                return int((end - start).total_seconds() * 1000)
            except Exception:
                return None
        return None

    def _summarize_observations(self, observations: list[Any]) -> list[dict] | None:
        if not observations:
            return None
        summary = []
        for obs in observations[:20]:
            item: dict[str, Any] = {
                "name": getattr(obs, "name", ""),
                "type": getattr(obs, "type", ""),
            }
            model = getattr(obs, "model", None)
            if model:
                item["model"] = model
            usage = getattr(obs, "usage", None)
            if usage:
                total = getattr(usage, "total", None)
                if total:
                    item["total_tokens"] = total
            summary.append(item)
        return summary
