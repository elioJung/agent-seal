import logging

import httpx

from notary_sdk.types import TracePayload

logger = logging.getLogger(__name__)


class NotaryClient:
    def __init__(self, api_key: str, server_url: str = "http://localhost:8000"):
        self._api_key = api_key
        self._server_url = server_url.rstrip("/")

    async def send_trace(self, payload: TracePayload) -> None:
        """서버로 트레이스를 전송한다. 실패해도 호출자를 블로킹하지 않는다."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    f"{self._server_url}/v1/traces",
                    json={"agent_id": payload.agent_id, "data": payload.data},
                    headers={"X-API-Key": self._api_key},
                )
                resp.raise_for_status()
        except Exception as exc:
            logger.warning("[notary-sdk] trace send failed (silent): %s", exc)
