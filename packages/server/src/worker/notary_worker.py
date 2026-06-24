import asyncio
import json
import logging
import uuid

from src.db import async_session, get_redis
from src.repository.trace import TraceRepository

logger = logging.getLogger(__name__)

STREAM = "notary:traces"
GROUP = "notary-workers"
CONSUMER = "worker-1"


async def run() -> None:
    redis = get_redis()

    try:
        await redis.xgroup_create(STREAM, GROUP, id="0", mkstream=True)
    except Exception:
        pass  # 이미 존재하면 무시

    logger.info("[notary-worker] started — consuming stream %s", STREAM)

    while True:
        try:
            results = await redis.xreadgroup(
                GROUP, CONSUMER, {STREAM: ">"}, count=10, block=1000
            )
            if not results:
                continue

            for _stream, messages in results:
                for msg_id, data in messages:
                    try:
                        await _process(data)
                        await redis.xack(STREAM, GROUP, msg_id)
                    except Exception as exc:
                        logger.error("[notary-worker] msg %s failed: %s", msg_id, exc)

        except asyncio.CancelledError:
            logger.info("[notary-worker] shutting down")
            break
        except Exception as exc:
            logger.error("[notary-worker] error: %s", exc)
            await asyncio.sleep(1)


async def _process(data: dict) -> None:
    async with async_session() as db:
        await TraceRepository(db).create(
            trace_id=uuid.UUID(data["trace_id"]),
            api_key_id=uuid.UUID(data["api_key_id"]),
            agent_id=data["agent_id"],
            payload=json.loads(data["payload"]),
            hash=data["hash"],
        )
