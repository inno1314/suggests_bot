from aiogram import Router

from .admins import router as admins_router
from .users import router as users_router
from .chat_member import router as member_router
from .active_status import router as status_router

other_routers = Router()

other_routers.include_routers(status_router,
                              member_router,
                              admins_router,
                              users_router)

