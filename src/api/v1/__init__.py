from fastapi import APIRouter

from src.api.v1.resources import router as router_resources

router = APIRouter(prefix="/v1")
router.include_router(router_resources)

__all__ = ["router"]
