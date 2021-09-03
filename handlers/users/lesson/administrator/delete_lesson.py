from typing import Dict

from aiogram.dispatcher.filters import Command
from aiogram.types import Message, ParseMode
from aiogram_dialog import Dialog, Window, DialogManager, ChatEvent, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Back
from aiogram_dialog.widgets.text import Const, Multi, Format
from aiogram_dialog.widgets.when import Whenable

from filters import CheckRole
from handlers.users.lesson.getters import getter_lesson_by_lesson_code
from handlers.users.getters import getter_start_data
from handlers.users.common_handlers import wrong_handler
from loader import dp, registry
from states.lesson import DeleteLessonSG

# Handlers
from utils.db_api.commands.lesson import get_lesson_by_code
from utils.db_api.database import db
from utils.useful_functions import answer_and_delete, say_and_delete


async def number_handler(message: Message, dialog: Dialog, manager: DialogManager):
    lesson = await get_lesson_by_code(message.text)
    if lesson:
        manager.current_context().dialog_data["lesson_code"] = message.text
        manager.current_context().dialog_data["lesson_id"] = lesson.id
        manager.current_context().dialog_data["status"] = lesson.status
        await dialog.next(manager)
    else:
        await say_and_delete(message, "Такого занятия не существует")

# On_clickers

async def on_delete(call: ChatEvent, button: Button, manager: DialogManager):
    status = manager.current_context().dialog_data.get("status")
    lesson_id = manager.current_context().dialog_data.get("lesson_id")
    lesson_code = manager.current_context().dialog_data.get("lesson_code")
    deleting = await db.lessons.delete_one({"_id": lesson_id})
    if deleting.acknowledged:
        await call.message.edit_text(f"Занятие {lesson_code} успешно удалено.")
        await manager.done()
    else:
        await call.message.edit_text(f"Почему-то не получилось удалить занятие {lesson_code}.")

async def on_cancel(call: ChatEvent, button: Button, manager: DialogManager):
    await call.message.edit_text(f"Удаление занятия отменено.")
    await manager.done()

dialog = Dialog(
    Window(
        Const("Введите код занятия"),
        MessageInput(number_handler),
        Button(Const("Закрыть"), id="cancel", on_click=on_cancel),
        state=DeleteLessonSG.code
    ),
    Window(
        Multi(
            Format("⚪️ {code}", when=lambda data, w, m: data["status"] == "planned"),
            Format("🟡 {code}", when=lambda data, w, m: data["status"] == "actual"),
            Format("🟢 {code}", when=lambda data, w, m: data["status"] == "passed"),
            Format("*Название:* {title}"),
            Format("*Группа:* {group}"),
            Format("*Дата:* {date}"),
            Format("*Время:* {time}"),
            Format("*Преподаватель:* {teacher}"),
        ),
        Const("\nУдалить занятие?", when=lambda data, w, m: data["status"] == "planned"),
        Const("\nЭто занятие идет в данный момент. Его нельзя удалить.",
              when=lambda data, w, m: data["status"] == "actual"),
        Const("\nЭто занятие идет уже прошло. Его нельзя удалить.",
              when=lambda data, w, m: data["status"] == "passed"),
        MessageInput(wrong_handler),
        Button(Const("Удалить"), id="delete", on_click=on_delete, when=lambda data, w, m: data["status"] == "planned"),
        Back(Const("Назад"), when=lambda data, w, m: data["status"] != "planned"),
        Button(Const("Отменить"), id="cancel", on_click=on_cancel),
        state=DeleteLessonSG.confirm,
        parse_mode=ParseMode.MARKDOWN,
        getter=getter_lesson_by_lesson_code
    ),
)

@dp.message_handler(Command(commands="deleteLesson"), CheckRole("administrator"))
async def delete_lesson(message: Message, dialog_manager: DialogManager):
    data = await getter_start_data(dialog_manager)
    await dialog_manager.start(DeleteLessonSG.code, data=data, mode=StartMode.RESET_STACK)

registry.register(dialog)