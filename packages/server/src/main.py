from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db import init_connections
from src.api.v1 import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_connections()
    yield


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
