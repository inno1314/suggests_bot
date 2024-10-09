__all__ = ("router",)

from aiogram import Router

from filters import isAdmin, isAdminQuery

from .start import router as start_router
from .help import router as help_router
from .recieve_actions import router as recieve_router
from .edit_before_send import router as edit_router
from .clean_feed import router as clean_router
from .ok_button import router as ok_router
from .ban_list import router as banlist_router
from .remove_kb import router as remove_kb_router

router = Router(name=__name__)
router.message.filter(isAdmin())
router.callback_query.filter(isAdminQuery())

router.include_routers(start_router,
                       help_router,
                       clean_router,
                       recieve_router,
                       edit_router,
                       ok_router,
                       banlist_router,
                       remove_kb_router)

