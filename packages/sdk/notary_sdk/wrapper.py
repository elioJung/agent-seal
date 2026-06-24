import asyncio
import logging
import time
from typing import Any

from notary_sdk.client import NotaryClient
from notary_sdk.types import TracePayload

logger = logging.getLogger(__name__)


class NotaryWrapper:
    """에이전트를 감싸 행동 트레이스를 자동으로 공증소로 전송한다.

    Usage:
        agent = NotaryWrapper(
            your_agent,
            api_key="nk_...",
            server_url="https://notary.example.com",
            task_name="문서 요약",
            tags=["production", "summary"],
        )
        result = agent.invoke({"input": "hello"})
    """

    def __init__(
        self,
        agent: Any,
        *,
        api_key: str,
        server_url: str = "http://localhost:8000",
        task_name: str | None = None,
        tags: list[str] | None = None,
        extra: dict[str, Any] | None = None,
    ):
        self._agent = agent
        self._client = NotaryClient(api_key=api_key, server_url=server_url)
        self._agent_id = getattr(agent, "name", type(agent).__name__)
        self._task_name = task_name
        self._tags = tags or []
        self._extra = extra or {}

    def invoke(self, input: Any, **kwargs: Any) -> Any:
        start = time.monotonic()
        result = self._agent.invoke(input, **kwargs)
        latency_ms = int((time.monotonic() - start) * 1000)
        self._fire_and_forget(input, result, latency_ms)
        return result

    async def ainvoke(self, input: Any, **kwargs: Any) -> Any:
        start = time.monotonic()
        result = await self._agent.ainvoke(input, **kwargs)
        latency_ms = int((time.monotonic() - start) * 1000)
        asyncio.create_task(self._send_trace(input, result, latency_ms))
        return result

    def _fire_and_forget(self, input: Any, result: Any, latency_ms: int) -> None:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(self._send_trace(input, result, latency_ms))
            else:
                loop.run_until_complete(self._send_trace(input, result, latency_ms))
        except Exception as exc:
            logger.warning("[notary-sdk] fire-and-forget failed: %s", exc)

    async def _send_trace(self, input: Any, result: Any, latency_ms: int) -> None:
        data: dict[str, Any] = {
            "input": str(input),
            "output": str(result),
            "latency_ms": latency_ms,
            **self._extra,
        }
        if self._task_name:
            data["task_name"] = self._task_name
        if self._tags:
            data["tags"] = self._tags

        payload = TracePayload(agent_id=self._agent_id, data=data)
        await self._client.send_trace(payload)
