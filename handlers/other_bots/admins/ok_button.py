from aiogram import types, Router, F

router = Router()

@router.callback_query(F.data == "OK")
async def ok_pressed(call: types.CallbackQuery):
    await call.message.delete()
