from fastapi import APIRouter

from core.config import setting

TG_PORT = setting.config_tg.port
router = APIRouter()


@router.api_route("/", methods=["GET", "HEAD"])
async def health():
    return {"status": "bot is running"}
