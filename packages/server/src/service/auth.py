import base64
import hashlib
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models.user import User
from src.repository.api_key import ApiKeyRepository
from src.repository.user import UserRepository
from src.utils.crypto import generate_api_key


def _prepare(password: str) -> bytes:
    """SHA-256 → base64 (44 bytes)로 변환해 bcrypt 72바이트 제한을 우회한다."""
    return base64.b64encode(hashlib.sha256(password.encode()).digest())


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(_prepare(password), bcrypt.gensalt(12)).decode()


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(_prepare(plain), hashed.encode())


async def register(db: AsyncSession, email: str, password: str) -> tuple[User, str]:
    repo = UserRepository(db)
    if await repo.get_by_email(email):
        raise ValueError("이미 등록된 이메일입니다")

    user = await repo.create(email, _hash_password(password))

    raw_key, key_hash, prefix = generate_api_key()
    await ApiKeyRepository(db).create(user.id, key_hash, prefix)

    return user, raw_key


async def login(db: AsyncSession, email: str, password: str) -> str:
    repo = UserRepository(db)
    user = await repo.get_by_email(email)
    if not user or not _verify_password(password, user.password_hash):
        raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다")

    payload = {
        "sub": str(user.id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")
