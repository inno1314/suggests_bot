__all__ = ("router",)

from aiogram import Router
from filters import isUser

from .start import router as start_router
from .suggest import router as suggest_router

router = Router(name=__name__)
router.message.filter(isUser())

router.include_routers(start_router,
                       suggest_router)

