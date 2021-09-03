from datetime import date
from operator import itemgetter

from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery, ParseMode
from aiogram_dialog import Window, Dialog, DialogManager, StartMode, ChatEvent
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Back, Group, Select, Calendar
from aiogram_dialog.widgets.text import Const, Multi, Format

from filters import CheckRole
from handlers.users.lesson.getters import getter_teachers_by_school_id
from handlers.users.lesson.getters_final_data import getter_final_data_add_lesson
from handlers.users.getters import getter_start_data, getter_schools_by_admin_id, getter_groups_by_school_id
from handlers.users.common_handlers import wrong_handler, on_cancel
from states.lesson import AddLessonSG
from loader import dp, registry
from utils.db_api.commands.school import get_school
from utils.db_api.database import db
from utils.db_api.models import Lesson
from utils.useful_functions import say_and_delete

# Handlers

async def title_handler(message: Message, dialog: Dialog, manager: DialogManager):
    manager.current_context().dialog_data["title"] = message.text
    await dialog.next(manager)


# On_clickers

async def on_school(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    school = await get_school(item_id)
    manager.current_context().dialog_data["school_id"] = item_id
    manager.current_context().dialog_data["school_name"] = school.name
    await manager.dialog().next(manager)


async def on_group(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    manager.current_context().dialog_data["group_id"] = item_id
    await manager.dialog().next(manager)


async def on_teacher(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    manager.current_context().dialog_data["teacher_id"] = item_id
    await manager.dialog().next(manager)


async def on_date(call: CallbackQuery, widget, manager: DialogManager, selected_date: date):
    date = str(selected_date)
    year = date.split("-")[0]
    month = date.split("-")[1]
    day = date.split("-")[2]
    manager.current_context().dialog_data["year"] = year
    manager.current_context().dialog_data["month"] = month
    manager.current_context().dialog_data["day"] = day
    await manager.dialog().next(manager)


async def on_time(call: ChatEvent, button: Button, manager: DialogManager):
    time = manager.event.data
    hour = time.split("_")[0]
    minute = time.split("_")[1]
    manager.current_context().dialog_data["hour"] = hour
    manager.current_context().dialog_data["minute"] = minute
    await manager.dialog().next(manager)


async def on_confirm(call: ChatEvent, button: Button, manager: DialogManager):
    result = await getter_final_data_add_lesson(manager)
    lesson_code = f"{result['day']}{result['month']}{result['year'][2]}{result['year'][3]}.{result['group']}"
    cursor = await db["lessons"].find_one({"code": lesson_code})
    if cursor:
        await say_and_delete(call.message, f"Такое занятие уже существует!", 4)
        return
    string_date = f"{result['year']}-{result['month']}-{result['day']}T{result['hour']}:{result['minute']}:00.000+03:00"
    new_lesson = Lesson(
        status="planned",
        code=lesson_code,
        title=result["title"],
        start=string_date,
        group=manager.current_context().dialog_data.get("group_id"),
        school=manager.current_context().dialog_data.get("school_id"),
        teacher=manager.current_context().dialog_data.get("teacher_id"),
    )
    await new_lesson.commit()
    await call.message.edit_text(f"Занятие *{lesson_code}* зарегистрировано!", parse_mode="MARKDOWN")
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
        state=AddLessonSG.school,
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
        state=AddLessonSG.group,
    ),
    Window(
        Const("Выберите преподавателя"),
        MessageInput(wrong_handler),
        Group(
            Select(
                Format("{item[1]}"),
                id="teacher",
                item_id_getter=itemgetter(0),
                items="teachers",
                on_click=on_teacher,
            ),
            width=2
        ),
        Back(Const("Назад")),
        state=AddLessonSG.teacher,
        getter=getter_teachers_by_school_id,
    ),
    Window(
        Const("Выберите дату занятия"),
        MessageInput(wrong_handler),
        Calendar(id='date', on_click=on_date),
        Back(Const("Назад")),
        state=AddLessonSG.date
    ),
    Window(
        Const("Выберите время начала"),
        MessageInput(wrong_handler),
        Group(*[
            Button(Const(text=f"{h % 24:2}:{m:02}"), id=f"{h}_{m:02}", on_click=on_time)
            for h in range(15, 21) for m in range(0, 60, 15)
        ], width=4),
        Back(Const("Назад")),
        state=AddLessonSG.time
    ),
    Window(
        Const("Введите название занятия"),
        MessageInput(title_handler),
        Back(Const("Назад")),
        state=AddLessonSG.title
    ),
    Window(
        Const(f"Давайте проверим информацию.\n"),
        Multi(
            Format("*Школа:* {school_name}"),
            Format("*Группа:* {group}"),
            Format("*Преподаватель:* {teacher}"),
            Format("*Дата:* {day}.{month}.{year}"),
            Format("*Время:* {hour}:{minute}"),
            Format("*Название:* {title}"),
        ),
        Button(text=Const("Подтвердить"), id="confirm", on_click=on_confirm),
        Back(Const("Назад")),
        state=AddLessonSG.confirm,
        parse_mode=ParseMode.MARKDOWN,
        getter=getter_final_data_add_lesson
    )
)


@dp.message_handler(Command(commands="addLesson"), CheckRole("administrator"))
async def add_lesson(message: Message, dialog_manager: DialogManager):
    data = await getter_start_data(dialog_manager)
    await dialog_manager.start(AddLessonSG.school, data=data, mode=StartMode.RESET_STACK)

registry.register(dialog)
