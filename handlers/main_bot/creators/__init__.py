from aiogram import Router
from filters import isBotCreator

from .show_menu import router as menu_router
from .show_income import router as income_router
from .edit_ads import router as ad_router
from .mailing import router as mailing_router
from .give_sub import router as give_sub_router

router = Router()
router.message.filter(isBotCreator())

router.include_routers(menu_router,
                       income_router,
                       ad_router,
                       give_sub_router,
                       mailing_router)

