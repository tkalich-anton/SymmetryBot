import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
from utils.useful_functions import answer_and_delete


@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    await answer_and_delete(
        message=message,
        text="Что-то для меня не понятное"
    )


# Эхо хендлер, куда летят ВСЕ сообщения с указанным состоянием
@dp.message_handler(state="*", content_types=types.ContentTypes.ANY)
async def bot_echo_all(message: types.Message, state: FSMContext):
    await answer_and_delete(
        message=message,
        text="Что-то для меня не понятное"
    )

