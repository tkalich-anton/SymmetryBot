from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandSettings

from filters import IsRegistered
from keyboards.inline.keyboard_generators import generate_inline_keyboard
from loader import dp
from utils.db_api.commands.user import get_user


@dp.message_handler(CommandSettings(), IsRegistered())
async def command_settings(message: types.Message, state: FSMContext):
    user = await get_user(telegram_id=message.from_user.id)
    await state.update_data({"command_message_id": message.message_id})
    answer = await message.answer(
        text=f"<b>НАСТРОЙКИ:</b>",
        reply_markup=generate_inline_keyboard([
            {"text": "Изменить имя", "callback_data": "change_first_name"},
            {"text": "Изменить фамилию", "callback_data": "change_last_name"},
            {"text": "Изменить почту", "callback_data": "change_email"},
            {"text": "Изменить Username", "callback_data": "change_email"},
            {"text": "Сбросить пароль", "callback_data": "change_name"},
            {"text": "Назад", "callback_data": "change_name"}
        ])
    )

    await state.update_data({"answer_message_id": answer.message_id})
