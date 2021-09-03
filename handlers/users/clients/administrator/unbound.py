from operator import itemgetter

from aiogram.dispatcher.filters import Command
from aiogram.types import Message, ParseMode
from aiogram_dialog import Window, Dialog, DialogManager, StartMode, ChatEvent
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Back, Group, Select
from aiogram_dialog.widgets.text import Const, Format, Jinja

from filters import CheckRole
from handlers.users.clients.getters import getter_final_data_unbound, getter_students
from handlers.users.common_handlers import on_cancel, wrong_handler
from states.clients import UnboundSG
from utils.db_api.commands.parent import get_students_by_parent, get_parent
from handlers.users.getters import getter_start_data
from loader import dp, registry, bot
from utils.db_api.commands.student import get_student, get_students

# On_clickers

async def on_student(c: ChatEvent, select: Select, manager: DialogManager, item_id):
    student = await get_student(telegram_id=item_id)
    manager.current_context().dialog_data["student_telegram_id"] = student.telegram_id
    manager.current_context().dialog_data["student_full_name"] = student.full_name
    await manager.dialog().next(manager)

async def on_unbound(call: ChatEvent, button: Button, manager: DialogManager):
    student_id = manager.current_context().dialog_data.get("student_telegram_id")
    student = await get_student(telegram_id=student_id)
    parent_id = student.parent.pk
    student.parent = None
    unbounding = await student.commit()
    if unbounding.acknowledged:
        parent = await get_parent(parent_id=parent_id)
        await call.message.edit_text(f"От студента *{student.full_name}* "
                                     f"успешно отвязан родитель *{parent.full_name}*.",
                                     parse_mode=ParseMode.MARKDOWN)
        try:
            await bot.send_message(chat_id=parent.telegram_id, text=f"От вас отвязан ученик {student.full_name}.")
            await bot.send_message(chat_id=student.telegram_id, text=f"От вас отвязан родитель {parent.full_name}.")
        finally:
            await manager.done()
    else:
        await call.message.edit_text(f"Что-то пошло не так.")
    await manager.done()

dialog = Dialog(
    Window(
        Const(text="Выберите студента, от которого хотите отвязать родителя.\n"),
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
        state=UnboundSG.student,
        parse_mode=ParseMode.HTML,
        getter=getter_students
    ),
    Window(
        Format(text="Выбранный студент:\n<b>{student_full_name} (ID {student_telegram_id})</b>\n"),
        Format(text="Привязанный родитель:\n<b>{parent_full_name} (ID {parent_telegram_id})</b>"),
        Const(text="\nОтвязать родителя?"),
        Button(Const("Отвязать родителя"), id="delete", on_click=on_unbound),
        Back(Const("Назад")),
        Button(Const("Отменить"), id="cancel", on_click=on_cancel),
        state=UnboundSG.confirm,
        parse_mode=ParseMode.HTML,
        getter=getter_final_data_unbound,
    )

)



@dp.message_handler(Command(commands="unbound"), CheckRole("administrator"))
async def unbound(message: Message, dialog_manager: DialogManager):
    data = await getter_start_data(dialog_manager, extra_data={
        "fs_parent_exist": True
    })
    await dialog_manager.start(UnboundSG.student, data=data, mode=StartMode.RESET_STACK)


registry.register(dialog)
