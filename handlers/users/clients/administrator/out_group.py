from operator import itemgetter

from aiogram.dispatcher.filters import Command
from aiogram.types import Message, ParseMode
from aiogram_dialog import DialogManager, StartMode, Dialog, Window, ChatEvent
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Back, Select, Group
from aiogram_dialog.widgets.text import Const, Format
from bson import ObjectId

from filters import CheckRole
from handlers.users.clients.getters import getter_students, getter_final_data_io_group
from handlers.users.common_handlers import on_cancel, wrong_handler
from handlers.users.getters import getter_start_data, getter_groups_by_school_id, getter_schools_by_admin_id
from loader import dp, registry, bot
from states.clients import InGroupSG, OutGroupSG
from utils.db_api.commands.school import get_group, get_school
from utils.db_api.commands.student import get_student

async def on_school(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    school = await get_school(item_id)
    manager.current_context().dialog_data["school_id"] = item_id
    manager.current_context().dialog_data["school_name"] = school.name
    await manager.dialog().next(manager)


async def on_group(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    group = await get_group(group_id=item_id)
    manager.current_context().dialog_data["group_id"] = ObjectId(item_id)
    manager.current_context().dialog_data["group_number"] = group.group_number
    await manager.dialog().next(manager)


async def on_student(c: ChatEvent, select: Select, manager: DialogManager, item_id):
    student = await get_student(telegram_id=int(item_id))
    manager.current_context().dialog_data["student_telegram_id"] = student.telegram_id
    manager.current_context().dialog_data["student_full_name"] = student.full_name
    await manager.dialog().next(manager)

async def on_confirm(call: ChatEvent, button: Button, manager: DialogManager):
    student_telegram_id = manager.current_context().dialog_data.get("student_telegram_id")
    student_full_name = manager.current_context().dialog_data.get("student_full_name")
    group_id = manager.current_context().dialog_data.get("group_id")
    student = await get_student(telegram_id=student_telegram_id)
    print(student)
    group = await get_group(group_id=group_id)
    student.groups.remove(group)
    removing = await student.commit()
    if removing.acknowledged:
        await call.message.edit_text(f"Студент *{student_full_name}* успешно исключен из *Группы {group.group_number}*.",
                                     parse_mode=ParseMode.MARKDOWN)
        try:
            await bot.send_message(chat_id=student.telegram_id, text=f"В исключены из *Группы {group.group_number}*.")
        finally:
            await manager.done()
    else:
        await call.message.edit_text(f"Что-то пошло не так.")
    await manager.done()

dialog = Dialog(
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
        state=OutGroupSG.school,
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
        state=OutGroupSG.group,
    ),
    Window(
        Const(text="Выберите студента, которого хотите исключить из группы.\n"),
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
        Back(Const("Назад")),
        state=OutGroupSG.student,
        parse_mode=ParseMode.HTML,
        getter=getter_students
    ),
    Window(
        Format(text="Выбранный студент:\n*{student_full_name} (ID {student_telegram_id})*\n\n"
                    "Выбранная группа:\n*Группа {group_number}*\n\n"
                    "Исключить студента из группы?"),
        Button(text=Const("Исключить"), id="confirm", on_click=on_confirm),
        Back(Const("Назад")),
        Button(Const("Закрыть"), id="cancel", on_click=on_cancel),
        state=OutGroupSG.confirm,
        parse_mode=ParseMode.MARKDOWN,
        getter=getter_final_data_io_group
    )

)

@dp.message_handler(Command(commands="outGroup"), CheckRole("administrator"))
async def out_group(message: Message, dialog_manager: DialogManager):
    data = await getter_start_data(dialog_manager)
    await dialog_manager.start(OutGroupSG.school, data=data, mode=StartMode.RESET_STACK)


registry.register(dialog)