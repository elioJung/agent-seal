from fastapi import APIRouter

from src.api.v1 import auth, certificates, traces, verify

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(traces.router, prefix="/traces", tags=["traces"])
router.include_router(certificates.router, prefix="/certificates", tags=["certificates"])
router.include_router(verify.router, prefix="/verify", tags=["verify"])
