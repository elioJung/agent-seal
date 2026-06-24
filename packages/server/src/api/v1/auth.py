from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.service import auth as auth_service

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        user, raw_key = await auth_service.register(db, body.email, body.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "user_id": str(user.id),
        "api_key": raw_key,
        "message": "API 키는 한 번만 표시됩니다. 반드시 복사해두세요.",
    }


@router.post("/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        token = await auth_service.login(db, body.email, body.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

    return {"access_token": token, "token_type": "bearer"}
