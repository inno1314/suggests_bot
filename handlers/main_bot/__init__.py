from aiogram import Router

from .users import router as users_router
from .premium import router as premium_router
from .creators import router as admins_router

main_router = Router()

main_router.include_routers(admins_router,
                            users_router,
                            premium_router)

