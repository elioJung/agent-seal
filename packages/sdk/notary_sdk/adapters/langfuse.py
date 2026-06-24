"""Langfuse 트레이스를 Notary data dict으로 변환하는 어댑터.

Langfuse 4.x 호환: lf.api.trace.get(trace_id)가 반환하는
TraceWithFullDetails 객체를 처리한다.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


class LangfuseAdapter:
    """Langfuse TraceWithFullDetails → Notary TracePayload data 변환.

    Usage:
        lf = Langfuse(public_key=..., secret_key=..., host=...)
        trace = lf.api.trace.get(trace_id)
        converted = LangfuseAdapter().convert(trace)
        await notary_client.send_trace(TracePayload(
            agent_id=converted["agent_id"],
            data=converted["data"],
        ))
    """

    def convert(self, langfuse_trace: Any) -> dict[str, Any]:
        observations = getattr(langfuse_trace, "observations", None) or []
        generations = [
            o for o in observations
            if getattr(o, "type", "").upper() == "GENERATION"
        ]

        usage = self._sum_usage(generations)
        latency_ms = self._extract_latency(langfuse_trace)
        model = self._primary_model(generations)
        obs_summary = self._summarize_observations(observations)

        data: dict[str, Any] = {
            "langfuse_trace_id": getattr(langfuse_trace, "id", None),
            "task_name": getattr(langfuse_trace, "name", None),
            "input": getattr(langfuse_trace, "input", None),
            "output": getattr(langfuse_trace, "output", None),
            "tags": getattr(langfuse_trace, "tags", []) or [],
            "session_id": getattr(langfuse_trace, "session_id", None),
            "user_id": getattr(langfuse_trace, "user_id", None),
            "metadata": getattr(langfuse_trace, "metadata", None) or {},
        }

        if latency_ms is not None:
            data["latency_ms"] = latency_ms
        if model:
            data["model"] = model
        if usage:
            data["usage"] = usage
        if obs_summary:
            data["observations"] = obs_summary

        return {
            "agent_id": getattr(langfuse_trace, "name", "unknown-agent"),
            "data": {k: v for k, v in data.items() if v is not None},
        }

    def _primary_model(self, generations: list[Any]) -> str | None:
        for gen in generations:
            model = getattr(gen, "model", None)
            if model:
                return model
        return None

    def _sum_usage(self, generations: list[Any]) -> dict[str, Any] | None:
        """모든 GENERATION 관측값의 토큰 사용량을 합산한다."""
        input_t = output_t = total_t = 0
        total_cost = 0.0
        has_data = False

        for gen in generations:
            usage = getattr(gen, "usage", None)
            if usage is None:
                continue
            inp = getattr(usage, "input", None) or 0
            out = getattr(usage, "output", None) or 0
            tot = getattr(usage, "total", None) or 0
            cost = getattr(usage, "total_cost", None) or 0.0
            if inp or out or tot:
                has_data = True
            input_t += inp
            output_t += out
            total_t += tot
            total_cost += cost

        if not has_data:
            return None

        result: dict[str, Any] = {
            "input_tokens": input_t,
            "output_tokens": output_t,
            "total_tokens": total_t,
        }
        if total_cost:
            result["total_cost"] = round(total_cost, 8)
        return result

    def _extract_latency(self, trace: Any) -> int | None:
        # Langfuse 4.x: trace.latency는 초 단위 float
        latency = getattr(trace, "latency", None)
        if latency is not None:
            try:
                return int(float(latency) * 1000)
            except (TypeError, ValueError):
                pass

        # 3.x fallback: timestamp와 end_time의 차이
        start = getattr(trace, "timestamp", None)
        end = getattr(trace, "end_time", None) or getattr(trace, "updatedAt", None)
        if start and end:
            try:
                return int((end - start).total_seconds() * 1000)
            except Exception:
                pass
        return None

    def _summarize_observations(self, observations: list[Any]) -> list[dict] | None:
        if not observations:
            return None
        summary = []
        for obs in observations[:20]:
            item: dict[str, Any] = {
                "name": getattr(obs, "name", "") or "",
                "type": getattr(obs, "type", "") or "",
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
