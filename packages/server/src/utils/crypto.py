import hashlib
import hmac
import json
import secrets
from typing import Any


def hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def generate_api_key() -> tuple[str, str, str]:
    """Returns (raw_key, key_hash, prefix)"""
    raw = f"nk_{secrets.token_urlsafe(24)}"
    return raw, hash_key(raw), raw[:8]


def hash_payload(agent_id: str, data: dict[str, Any]) -> str:
    payload_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(f"{agent_id}:{payload_str}".encode()).hexdigest()


def sign_hash(trace_hash: str, secret_key: str) -> str:
    return hmac.new(
        secret_key.encode(),
        trace_hash.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()
