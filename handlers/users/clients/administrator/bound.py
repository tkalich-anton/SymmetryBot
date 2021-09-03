from datetime import date
from operator import itemgetter

from aiogram.dispatcher.filters import Command
from aiogram.types import Message, ParseMode
from aiogram_dialog import Window, Dialog, DialogManager, StartMode, ChatEvent
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Back, Group, Select
from aiogram_dialog.widgets.text import Const, Format

from filters import CheckRole
from handlers.users.clients.getters import getter_parents, getter_final_data_bound, \
    getter_students
from handlers.users.common_handlers import on_cancel, wrong_handler
from states.clients import BoundSG
from utils.db_api.commands.parent import get_parent
from handlers.users.getters import getter_start_data
from loader import dp, registry, bot
from utils.db_api.commands.student import get_student


# On_clickers

async def on_bound(call: ChatEvent, button: Button, manager: DialogManager):
    student_telegram_id = manager.current_context().dialog_data.get("student_telegram_id")
    parent_telegram_id = manager.current_context().dialog_data.get("parent_telegram_id")
    student = await get_student(telegram_id=student_telegram_id)
    parent = await get_parent(telegram_id=parent_telegram_id)
    student.parent = parent.id
    bounding = await student.commit()
    if bounding.acknowledged:
        await call.message.edit_text(f"Студенту *{student.full_name}* успешно привязан родитель *{parent.full_name}*.",
                                     parse_mode=ParseMode.MARKDOWN)
        try:
            await bot.send_message(chat_id=parent.telegram_id, text=f"К вам привязан ученик {student.full_name}.")
            await bot.send_message(chat_id=student.telegram_id, text=f"К вам привязан родитель {parent.full_name}.")
        finally:
            await manager.done()
    else:
        await call.message.edit_text(f"Что-то пошло не так.")
    await manager.done()


async def on_student(c: ChatEvent, select: Select, manager: DialogManager, item_id):
    student = await get_student(telegram_id=item_id)
    manager.current_context().dialog_data["student_telegram_id"] = student.telegram_id
    manager.current_context().dialog_data["student_full_name"] = student.full_name
    await manager.dialog().next(manager)


async def on_parent(c: ChatEvent, select: Select, manager: DialogManager, item_id):
    parent = await get_parent(telegram_id=item_id)
    manager.current_context().dialog_data["parent_telegram_id"] = parent.telegram_id
    manager.current_context().dialog_data["parent_full_name"] = parent.full_name
    await manager.dialog().next(manager)


dialog = Dialog(
    Window(
        Const(text="Выберите студента, к которому хотите привязать родителя.\n"),
        Group(
            Select(
                Format("{item[1]} (ID {item[0]})"),
                id="students",
                item_id_getter=itemgetter(0),
                items="students",
                on_click=on_student,
            ),
            width=1,
        ),
        MessageInput(wrong_handler),
        Button(Const("Закрыть"), id="cancel", on_click=on_cancel),
        state=BoundSG.student,
        parse_mode=ParseMode.HTML,
        getter=getter_students
    ),
    Window(
        Format(text="Выберите родителя, к которому хотите привязать\n"
                    "<b>{student[full_name]} (ID {student[telegram_id]})</b>.\n"),
        Group(
            Select(
                Format("{item[1]} (ID {item[0]})"),
                id="parents",
                item_id_getter=itemgetter(0),
                items="parents",
                on_click=on_parent,
            ),
            width=1,
        ),
        Const(text="Введите Username родителя."),
        Back(Const("Назад")),
        MessageInput(wrong_handler),
        state=BoundSG.parent,
        parse_mode=ParseMode.HTML,
        getter=getter_parents,
    ),
    Window(
        Format(text="Выбранный студент:\n<b>{student_full_name} (ID {student_telegram_id})</b>"),
        Format(text="Выбранный родитель:\n<b>{parent_full_name} (ID {parent_telegram_id})</b>"),
        Const(text="\nСвязать?"),
        Button(Const("Связать"), id="delete", on_click=on_bound),
        Back(Const("Назад")),
        Button(Const("Отменить"), id="cancel", on_click=on_cancel),
        state=BoundSG.confirm,
        parse_mode=ParseMode.HTML,
        getter=getter_final_data_bound,
    )
)


@dp.message_handler(Command(commands="bound"), CheckRole("administrator"))
async def bound(message: Message, dialog_manager: DialogManager):
    data = await getter_start_data(dialog_manager, extra_data={
        "fs_parent_exist": False
    })
    await dialog_manager.start(BoundSG.student, data=data, mode=StartMode.RESET_STACK)


registry.register(dialog)
