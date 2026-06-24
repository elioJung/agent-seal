import asyncio
import logging
from typing import Any

from notary_sdk.client import NotaryClient
from notary_sdk.types import TracePayload

logger = logging.getLogger(__name__)


class NotaryWrapper:
    """에이전트를 감싸 행동 트레이스를 자동으로 공증소로 전송한다.

    Usage:
        agent = NotaryWrapper(your_agent, api_key="nk_...", server_url="https://notary.example.com")
        result = agent.invoke({"input": "hello"})
    """

    def __init__(self, agent: Any, *, api_key: str, server_url: str = "http://localhost:8000"):
        self._agent = agent
        self._client = NotaryClient(api_key=api_key, server_url=server_url)
        self._agent_id = getattr(agent, "name", type(agent).__name__)

    def invoke(self, input: Any, **kwargs: Any) -> Any:
        result = self._agent.invoke(input, **kwargs)
        self._fire_and_forget(input, result)
        return result

    async def ainvoke(self, input: Any, **kwargs: Any) -> Any:
        result = await self._agent.ainvoke(input, **kwargs)
        asyncio.create_task(self._send_trace(input, result))
        return result

    def _fire_and_forget(self, input: Any, result: Any) -> None:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(self._send_trace(input, result))
            else:
                loop.run_until_complete(self._send_trace(input, result))
        except Exception as exc:
            logger.warning("[notary-sdk] fire-and-forget failed: %s", exc)

    async def _send_trace(self, input: Any, result: Any) -> None:
        payload = TracePayload(
            agent_id=self._agent_id,
            data={"input": str(input), "output": str(result)},
        )
        await self._client.send_trace(payload)
