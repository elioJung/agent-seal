import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db import init_connections
from src.api.v1 import router as v1_router
from src.worker import notary_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_connections()
    worker_task = asyncio.create_task(notary_worker.run())
    yield
    worker_task.cancel()
    with suppress(asyncio.CancelledError):
        await worker_task


app = FastAPI(
    title="Agent Notary",
    version="0.1.0",
    description="AI 에이전트 행동에 해시 서명된 불변 로그와 증명서를 발급하는 인프라 레이어",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/v1")


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
