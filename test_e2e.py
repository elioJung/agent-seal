# -*- coding: utf-8 -*-
"""
Agent Notary E2E

  pip install httpx
  pip install -e packages/sdk
  python test_e2e.py
"""

import asyncio
import httpx
from notary_sdk import NotaryWrapper

SERVER = "http://localhost:8000"
TEST_EMAIL = "test-e2e@example.com"
TEST_PASSWORD = "notary-e2e-2026"


class MockAgent:
    name = "mock-research-agent"

    def invoke(self, input: dict) -> dict:
        query = input.get("query", "")
        return {"result": f"'{query}' 분석 완료", "confidence": 0.92}


async def register() -> str:
    async with httpx.AsyncClient(base_url=SERVER, timeout=10.0) as client:
        resp = await client.post("/v1/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        })
        if resp.status_code in (200, 201):
            api_key = resp.json()["api_key"]
            print(f"[OK] 가입 완료")
            print(f"     API Key: {api_key}")
            return api_key
        if resp.status_code == 400 and "이미 등록" in resp.text:
            raise RuntimeError(
                f"테스트 계정이 이미 존재합니다. 아래 명령으로 삭제 후 재시도:\n"
                f"  docker compose exec db psql -U notary -d notary -c "
                f"\"DELETE FROM api_keys WHERE user_id=(SELECT id FROM users WHERE email='{TEST_EMAIL}'); "
                f"DELETE FROM users WHERE email='{TEST_EMAIL}';\""
            )
        resp.raise_for_status()
        return ""


async def send_traces(api_key: str) -> None:
    agent = MockAgent()
    wrapped = NotaryWrapper(agent, api_key=api_key, server_url=SERVER)

    queries = [
        {"query": "기후 변화가 한국 농업에 미치는 영향"},
        {"query": "2026년 AI 트렌드 분석"},
        {"query": "양자 컴퓨팅의 현재 한계"},
    ]

    for q in queries:
        result = wrapped.invoke(q)
        print(f"[OK] invoke: {q['query'][:25]}")
        await asyncio.sleep(0.5)


async def verify_traces(api_key: str) -> None:
    async with httpx.AsyncClient(base_url=SERVER, timeout=10.0) as client:
        resp = await client.get("/v1/traces", headers={"X-API-Key": api_key})
        resp.raise_for_status()
        data = resp.json()
        total = data.get("total", 0)
        traces = data.get("items", [])

        print(f"\n[OK] 저장된 트레이스: {total}건")
        for t in traces[:5]:
            print(f"     {t['id'][:8]}... | agent={t['agent_id']} | {t['created_at'][:19]}")

        if not traces:
            print("[!!] 트레이스 없음 - 워커 로그 확인 필요")
            return

        first_id = traces[0]["id"]
        print(f"\n[>>] 증명서 발급: trace_id={first_id[:8]}...")
        cert_resp = await client.post(
            f"/v1/certificates/{first_id}",
            headers={"X-API-Key": api_key},
        )
        if cert_resp.status_code in (200, 201):
            cert = cert_resp.json()
            cert_id = cert.get("id") or cert.get("certificate_id", "")
            print(f"[OK] 증명서 발급 완료: {str(cert_id)[:8]}...")
            print(f"     검증 URL: http://localhost:5173/verify/{cert_id}")
        else:
            print(f"[!!] 증명서 발급 실패: {cert_resp.status_code} - {cert_resp.text[:120]}")


async def main():
    print("=" * 50)
    print("  Agent Notary E2E Test")
    print("=" * 50)

    api_key = await register()
    if not api_key:
        return

    print("\n[>>] 트레이스 전송 중...")
    await send_traces(api_key)

    print("\n[>>] 트레이스 조회 중...")
    await verify_traces(api_key)

    print("\n[DONE] E2E 완료!")
    print("  대시보드: http://localhost:5173")
    print("  위 API Key 입력 후 트레이스 목록 확인")


if __name__ == "__main__":
    asyncio.run(main())
