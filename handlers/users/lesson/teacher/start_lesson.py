from datetime import datetime
from operator import itemgetter

import pytz
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, ParseMode
from aiogram_dialog import DialogManager, StartMode, Dialog, Window, ChatEvent
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Back, Select, Group, Multiselect, Next
from aiogram_dialog.widgets.text import Const, Format, Jinja
from bson import ObjectId

from filters import CheckRole
from handlers.users.common_handlers import wrong_handler, on_cancel
from handlers.users.getters import getter_start_data, getter_schools_by_teacher_id, getter_groups_by_school_id
from handlers.users.lesson.getters import getter_lessons, getter_lesson_by_lesson_code
from handlers.users.lesson.getters_final_data import getter_final_data_start_lesson
from loader import dp, registry
from states.lesson import DeleteLessonSG, StartLessonSG
from utils.db_api.commands.lesson import get_lesson_by_code
from utils.db_api.commands.school import get_school
from utils.db_api.commands.student import get_student


async def on_school(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    school = await get_school(item_id)
    manager.current_context().dialog_data["teacher_id"] = manager.current_context().start_data["teacher_id"]
    manager.current_context().dialog_data["school_id"] = ObjectId(item_id)
    manager.current_context().dialog_data["school_name"] = school.name
    await manager.dialog().next(manager)

async def on_group(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    manager.current_context().dialog_data["group_id"] = ObjectId(item_id)
    manager.current_context().dialog_data["lesson_status"] = "planned"
    await manager.dialog().next(manager)

async def on_lesson(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    manager.current_context().dialog_data["lesson_code"] = item_id
    await manager.dialog().next(manager)

async def on_confirm(call: ChatEvent, button: Button, manager: DialogManager):
    lesson_code = manager.current_context().dialog_data.get("lesson_code")
    lesson = await get_lesson_by_code(lesson_code=lesson_code)
    lesson.status = "actual"
    timezone = pytz.timezone("Europe/Moscow")
    lesson.started_at = datetime.now(tz=timezone)
    for student_telegram_id in manager.current_context().widget_data.get("students"):
        student = await get_student(telegram_id=int(student_telegram_id))
        lesson.in_time.append(student.id)
    starting = await lesson.commit()
    if starting.acknowledged:
        await call.message.edit_text(f"Занятие *{lesson_code}* началось. Удачи!",
                                     parse_mode=ParseMode.MARKDOWN)
    await manager.done()
students_list = Jinja("""
{% for student in students %}
{{ student.full_name }} (ID {{ student.telegram_id }})
{% endfor %}
""")

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
        getter=getter_schools_by_teacher_id,
        state=StartLessonSG.school,
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
        state=StartLessonSG.group,
    ),
    Window(
        Const("Выберите занятие"),
        MessageInput(wrong_handler),
        Group(
            Select(
                Format("Занятие {item[code]}"),
                id="lesson",
                item_id_getter=itemgetter("code"),
                items="lessons",
                on_click=on_lesson,
            ),
            width=2
        ),
        Back(Const("Назад")),
        getter=getter_lessons,
        state=StartLessonSG.lesson,
    ),
    Window(
        MessageInput(wrong_handler),
        Const("Выберите студентов, которые на занятии."),
        Group(
            Multiselect(
                Format("✔️ {item[full_name]}"),
                Format("✖️ {item[full_name]}"),
                id="students",
                item_id_getter=itemgetter("telegram_id"),
                items="students",
            ),
            width=1
        ),
        Next(Const("Продолжить")),
        Back(Const("Назад")),
        getter=getter_lesson_by_lesson_code,
        state=StartLessonSG.students,
    ),
    Window(
        Format("Выбранное занятие:\n*{lesson_code}*."),
        Format("Тема занятия:\n*{lesson_theme}*."),
        Const("Студенты на занятии:"),
        students_list,
        Const("Начать занятие?"),
        Button(text=Const("Начать занятие"), id="confirm", on_click=on_confirm),
        Back(Const("Назад")),
        MessageInput(wrong_handler),
        getter=getter_final_data_start_lesson,
        state=StartLessonSG.confirm,
        parse_mode=ParseMode.MARKDOWN,
    )
)


@dp.message_handler(Command(commands="startLesson"), CheckRole("teacher"))
async def start_lesson(message: Message, dialog_manager: DialogManager):
    data = await getter_start_data(dialog_manager)
    await dialog_manager.start(StartLessonSG.school, data=data, mode=StartMode.RESET_STACK)

registry.register(dialog)
