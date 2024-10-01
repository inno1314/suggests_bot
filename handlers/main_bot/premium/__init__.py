__all__ = ("router",)

from aiogram import Router
from filters import isSub

from .multi_control import router as multi_control_router
from .post_formatting import router as formatting_router

router = Router(name=__name__)
router.callback_query.filter(isSub())

router.include_routers(multi_control_router,
                       formatting_router)

