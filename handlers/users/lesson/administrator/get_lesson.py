from datetime import date
from operator import itemgetter

from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery, ParseMode
from aiogram_dialog import Window, Dialog, DialogManager, StartMode, ChatEvent
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Back, Group, Select, Calendar, SwitchTo
from aiogram_dialog.widgets.text import Const, Multi, Format, Jinja

from filters import CheckRole
from handlers.users.common_handlers import wrong_handler
from utils.db_api.commands.school import get_school
from handlers.users.lesson.getters import getter_lessons
from handlers.users.getters import getter_start_data, getter_schools_by_admin_id
from states.lesson import GetLessonSG
from loader import dp, registry


# On_clickers

async def on_period(call: ChatEvent, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(GetLessonSG.date_from, manager)


async def on_school(call: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    school = await get_school(item_id)
    manager.current_context().dialog_data["school_id"] = item_id
    manager.current_context().dialog_data["school_name"] = school.name
    await manager.dialog().next(manager)


async def on_current_week(call: ChatEvent, button: Button, manager: DialogManager):
    manager.current_context().dialog_data["period"] = "current_week"
    await manager.dialog().switch_to(GetLessonSG.get_lessons, manager)


async def on_next_week(call: ChatEvent, button: Button, manager: DialogManager):
    manager.current_context().dialog_data["period"] = "next_week"
    await manager.dialog().switch_to(GetLessonSG.get_lessons, manager)


async def on_current_month(call: ChatEvent, button: Button, manager: DialogManager):
    manager.current_context().dialog_data["period"] = "current_month"
    await manager.dialog().switch_to(GetLessonSG.get_lessons, manager)


async def on_next_month(call: ChatEvent, button: Button, manager: DialogManager):
    manager.current_context().dialog_data["period"] = "next_month"
    await manager.dialog().switch_to(GetLessonSG.get_lessons, manager)


async def on_interval(call: ChatEvent, button: Button, manager: DialogManager):
    manager.current_context().dialog_data["period"] = "interval"
    await manager.dialog().switch_to(GetLessonSG.date_from, manager)


async def on_date_from(call: CallbackQuery, widget, manager: DialogManager, selected_date: date):
    manager.current_context().dialog_data["date_from"] = str(selected_date)
    await manager.dialog().switch_to(GetLessonSG.date_to, manager)


async def on_date_to(call: CallbackQuery, widget, manager: DialogManager, selected_date: date):
    manager.current_context().dialog_data["date_to"] = str(selected_date)
    await manager.dialog().switch_to(GetLessonSG.get_lessons, manager)


async def on_cancel(call: ChatEvent, button: Button, manager: DialogManager):
    await call.message.delete()
    await manager.done()


async def on_close(call: ChatEvent, button: Button, manager: DialogManager):
    await manager.done()


lesson_text = Jinja("""
{% for lesson in lessons %}
{% if lesson.status == "planned" %}⚪️{% endif %}
{% if lesson.status == "actual" %}🟡{% endif %}
{% if lesson.status == "passed" %}🟢{% endif %} <b>{{ lesson.code }}</b>
Дата занятия: {{ lesson.date }}
Группа: {{ lesson.group }}
Время начала: {{ lesson.time }}
Преподаватель: {{ lesson.teacher }}
{{ ' ' }}
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
        getter=getter_schools_by_admin_id,
        state=GetLessonSG.school,
    ),
    Window(
        Const("Выберите период, за который хотите посмотреть занятия"),
        MessageInput(wrong_handler),
        Group(
            Button(Const("Текущая неделя"), id="current_week", on_click=on_current_week),
            Button(Const("Текущий месяц"), id="current_month", on_click=on_current_month),
            Button(Const("Следующая неделя"), id="next_week", on_click=on_next_week),
            Button(Const("Следующий месяц"), id="next_month", on_click=on_next_month),
            Button(Const("Выбрать интервал"), id="interval", on_click=on_interval),
            width=2
        ),
        Back(Const("Назад")),
        state=GetLessonSG.period,
    ),
    Window(
        Const("С какой даты искать занятия?"),
        MessageInput(wrong_handler),
        Calendar(id="date", on_click=on_date_from),
        SwitchTo(Const("Назад"), id="to_period", state=GetLessonSG.period),
        state=GetLessonSG.date_from
    ),
    Window(
        Const("По какую дату искать занятия?"),
        MessageInput(wrong_handler),
        Calendar(id='date', on_click=on_date_to),
        Back(Const("Назад")),
        state=GetLessonSG.date_to
    ),
    Window(
        Multi(
            Const(text="Выбран период:"),
            Format("с {date_from} по {date_to}"),
            sep="\n"
        ),
        lesson_text,
        MessageInput(wrong_handler),
        SwitchTo(Const("Назад"), id="to_period", state=GetLessonSG.period),
        Button(Const("Закрыть"), id="cancel", on_click=on_close),
        parse_mode=ParseMode.HTML,
        state=GetLessonSG.get_lessons,
        getter=getter_lessons
    )
)


@dp.message_handler(Command(commands="getLessons"), CheckRole("administrator"))
async def get_lessons(message: Message, dialog_manager: DialogManager):
    data = await getter_start_data(dialog_manager)
    await dialog_manager.start(GetLessonSG.school, data=data, mode=StartMode.RESET_STACK)


registry.register(dialog)
