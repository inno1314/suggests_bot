__all__ = ("router",)

from aiogram import Router
from filters import isSub

from .multi_control import router as multi_control_router
from .bot_formatting import router as bot_formatting_router
from .change_formatting import router as change_formatting_router

router = Router(name=__name__)
router.callback_query.filter(isSub())

router.include_routers(multi_control_router,
                       bot_formatting_router,
                       change_formatting_router)

