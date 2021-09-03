from operator import itemgetter

from aiogram.dispatcher.filters import Command
from aiogram.types import Message, ParseMode
from aiogram_dialog import DialogManager, StartMode, Dialog, Window, ChatEvent
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Back, Select, Group, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Jinja, Format

from filters import CheckRole
from handlers.users.clients.getters import getter_students, getter_final_data_io_group
from handlers.users.common_handlers import on_cancel, wrong_handler
from handlers.users.getters import getter_start_data, getter_schools_by_admin_id, getter_groups_by_school_id
from loader import dp, registry, bot
from states.clients import InGroupSG
from utils.db_api.commands.school import get_school, get_group
from utils.db_api.commands.student import get_student

async def on_student(c: ChatEvent, select: Select, manager: DialogManager, item_id):
    student = await get_student(telegram_id=int(item_id))
    manager.current_context().dialog_data["student_telegram_id"] = student.telegram_id
    manager.current_context().dialog_data["student_full_name"] = student.full_name
    await manager.dialog().next(manager)

async def on_school(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    school = await get_school(item_id)
    manager.current_context().dialog_data["school_id"] = item_id
    manager.current_context().dialog_data["school_name"] = school.name
    await manager.dialog().next(manager)


async def on_group(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    group = await get_group(group_id=item_id)
    manager.current_context().dialog_data["group_id"] = item_id
    manager.current_context().dialog_data["group_number"] = group.group_number
    await manager.dialog().next(manager)

async def on_confirm(call: ChatEvent, button: Button, manager: DialogManager):
    student_telegram_id = manager.current_context().dialog_data.get("student_telegram_id")
    student_full_name = manager.current_context().dialog_data.get("student_full_name")
    group_id = manager.current_context().dialog_data.get("group_id")
    student = await get_student(telegram_id=student_telegram_id)
    group = await get_group(group_id=group_id)
    if student.groups:
        student.groups.append(group.id)
    else:
        student.groups = [group.id]
    student.confirmed = True
    addition = await student.commit()
    if addition.acknowledged:
        await call.message.edit_text(f"Студент *{student_full_name}* успешно добавлен в *Группу {group.group_number}*.",
                                     parse_mode=ParseMode.MARKDOWN)
        try:
            await bot.send_message(chat_id=student.telegram_id, text=f"В добавлены в *Группу {group.group_number}*.")
        finally:
            await manager.done()
    else:
        await call.message.edit_text(f"Что-то пошло не так.")

dialog = Dialog(
    Window(
        Const(text="Выберите студента, которого хотите добавить в группу.\n"),
        Group(
            Select(
                Format("{item[1]} (ID {item[0]})"),
                id="student",
                item_id_getter=itemgetter(0),
                items="students",
                on_click=on_student,
            ),
            width=1,
        ),
        MessageInput(wrong_handler),
        Button(Const("Закрыть"), id="cancel", on_click=on_cancel),
        state=InGroupSG.student,
        parse_mode=ParseMode.HTML,
        getter=getter_students
    ),
    Window(
        Const("Выберите школу"),
        MessageInput(wrong_handler),
        Group(
            Select(
                Format("{item[1]}"),
                id="school",
                item_id_getter=itemgetter(0),
                items="schools",
                on_click=on_school,
            ),
            width=2
        ),
        Button(Const("Закрыть"), id="cancel", on_click=on_cancel),
        getter=getter_schools_by_admin_id,
        state=InGroupSG.school,
    ),
    Window(
        Const("Выберите группу"),
        MessageInput(wrong_handler),
        Group(
            Select(
                Format("Группа {item[1]}"),
                id="group",
                item_id_getter=itemgetter(0),
                items="groups",
                on_click=on_group,
            ),
            width=2
        ),
        Back(Const("Назад")),
        getter=getter_groups_by_school_id,
        state=InGroupSG.group,
    ),
    Window(
        Format(text="Выбранный студент:\n*{student_full_name} (ID {student_telegram_id})*\n\n"
                    "Выбранная группа:\n*Группа {group_number}*\n\n"
                    "Добавить студента в группу?"),
        Button(text=Const("Добавить"), id="confirm", on_click=on_confirm),
        Back(Const("Назад")),
        Button(Const("Закрыть"), id="cancel", on_click=on_cancel),
        state=InGroupSG.confirm,
        parse_mode=ParseMode.MARKDOWN,
        getter=getter_final_data_io_group
    )

)

@dp.message_handler(Command(commands="inGroup"), CheckRole("administrator"))
async def in_group(message: Message, dialog_manager: DialogManager):
    data = await getter_start_data(dialog_manager)
    await dialog_manager.start(InGroupSG.student, data=data, mode=StartMode.RESET_STACK)


registry.register(dialog)