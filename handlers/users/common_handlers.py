from aiogram.types import Message
from aiogram_dialog import ChatEvent, DialogManager, Dialog
from aiogram_dialog.widgets.kbd import Button

from utils.useful_functions import say_and_delete


async def on_cancel(call: ChatEvent, button: Button, manager: DialogManager):
    await call.message.edit_text(f"Отменено.")
    await manager.done()


async def wrong_handler(message: Message, dialog: Dialog, manager: DialogManager):
    await say_and_delete(message, f"Я вас не понимаю", 2)