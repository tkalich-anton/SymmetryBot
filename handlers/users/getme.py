import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, ContentTypes, Message

from filters import IsRegistered
from keyboards.inline.callback_datas import inline_command_callback
from keyboards.inline.keyboard_generators import generate_inline_keyboard
from loader import dp, bot
from utils.db_api.commands.user import get_user
from utils.db_api.commands.role import get_roles_by_user
from utils.useful_functions import answer_and_delete


@dp.message_handler(Command(commands="getMe"), IsRegistered())
async def command_settings(message: Message, state: FSMContext):
    user = await get_user(telegram_id=message.from_user.id)
    if user:
        roles = await get_roles_by_user(user)
        if len(roles) == 1:
            answer = await message.answer(
                f"Вас зовут {user['full_name']}\n"
                f"Ваша роль: {roles[0]['name']}\n",
                reply_markup=generate_inline_keyboard([
                    {"text": "Понятно", "callback_data": "got_it"}
                ])
            )
        elif len(roles) > 1:
            text = ""
            for role in roles:
                text += f"- {role['name']} \n"
            answer = await message.answer(
                f"Вас зовут {user['full_name']}\n"
                f"Ваши роли:\n{text}",
                reply_markup=generate_inline_keyboard([
                    {"text": "Понятно", "callback_data": "got_it"}
                ])
            )
    await state.set_state("InGetMe")
    await state.update_data({"command_message_id": message.message_id})
    await state.update_data({"answer_message_id": answer.message_id})

@dp.callback_query_handler(text="got_it", state="InGetMe")
async def delete_call(call: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    await bot.delete_message(message_id=state_data["command_message_id"], chat_id=call.from_user.id)
    await bot.delete_message(message_id=state_data["answer_message_id"], chat_id=call.from_user.id)
    await state.finish()
    await call.answer()


@dp.message_handler(state="InGetMe", content_types=ContentTypes.ANY)
async def invalid_text(message: Message):
    await answer_and_delete(message=message, text=f"Нажмите кнопку «Понятно»")