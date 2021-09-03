from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from filters.permission import IsRegistered, IsUnregistered
from keyboards.inline.keyboard_generators import generate_inline_keyboard
from loader import dp, bot
from utils.db_api.commands.user import get_user
from utils.db_api.commands.role import get_roles_by_user


@dp.message_handler(CommandStart(), IsRegistered())
async def bot_start(message: types.Message):
    user = await get_user(telegram_id=message.from_user.id)
    if user:
        await message.answer(
            f"Привет, {user['first_name']}!\n\n"
            f"Вот список доступных вам команд:\n\n"
            f"/getMe\n"
        )


@dp.message_handler(CommandStart(), IsUnregistered())
async def bot_start(message: types.Message):
    await bot.delete_my_commands()
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        f"Вы не зарегистрированный пользователь. Хотите пройти регистрацию?",
        reply_markup=generate_inline_keyboard([
            {"text": "🚀Начать регистрацию", "callback_data": "start_registration"}
        ])
    )