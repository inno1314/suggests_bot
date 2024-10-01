__all__ = ("router",)

from aiogram import Router

from .start import router as start_router
from .view_bots import router as view_bots_router
from .add_bot import router as add_bot_router
from .delete_bot import router as delete_bot_router
from .switch_bot_state import router as switch_state_router
from .back import router as back_router
from .settings import router as setts_router
from .get_subscription import router as get_sub
from .ok_button import router as ok_router

router = Router(name=__name__)

router.include_routers(start_router,
                       view_bots_router,
                       add_bot_router,
                       delete_bot_router,
                       switch_state_router,
                       back_router,
                       setts_router,
                       get_sub,
                       ok_router)

