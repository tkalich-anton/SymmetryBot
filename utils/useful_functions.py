import asyncio

from aiogram.types import Message


async def answer_and_delete(message: Message, text: str, delay=3, disable_notification=True):
    answer = await message.answer(text=text, disable_notification=disable_notification)
    await asyncio.sleep(delay)
    await message.delete()
    await answer.delete()


async def say_and_delete(message: Message, text: str, delay=3, disable_notification=True):
    answer = await message.answer(text=text, disable_notification=disable_notification)
    await asyncio.sleep(delay)
    await answer.delete()