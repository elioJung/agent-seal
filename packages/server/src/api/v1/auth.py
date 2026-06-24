from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", status_code=201)
async def register(body: RegisterRequest) -> dict:
    # TODO Phase 2: 사용자 생성 + API Key 자동 발급
    return {"message": "TODO: implement register"}


@router.post("/login")
async def login(body: LoginRequest) -> dict:
    # TODO Phase 2: JWT 발급
    return {"message": "TODO: implement login"}
