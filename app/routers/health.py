from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

@router.get('/', summary="Health check")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}