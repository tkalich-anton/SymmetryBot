from typing import Dict

from aiogram.dispatcher.filters import Command
from aiogram.types import Message, ParseMode
from aiogram_dialog import DialogManager, StartMode, Dialog, Window, ChatEvent
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Keyboard
from aiogram_dialog.widgets.text import Const, Jinja, Multi
from aiogram_dialog.widgets.when import Whenable

from filters import IsRegistered
from states.menu import MenuSG
from .getters import getter_start_data
from loader import dp, registry

async def on_cancel(call: ChatEvent, button: Button, manager: DialogManager):
    await manager.done()

menu_text = Jinja("""
{% if admin_id %}
{% if count_roles > 1 %}
Команды для Администратора
{% endif %}
Создать занятие:
/createLesson
{{ ' ' }}
Посмотреть занятия:
/readLesson
{{ ' ' }}
Отредактировать занятие:
/editLesson
{{ ' ' }}
Удалить занятие:
/deleteLesson
{% endif %}
{% if teacher_id %}
{% if count_roles > 1 %}
Команды для Преподавателя
{% endif %}
{% endif %}
{% if curator_id %}
{% if count_roles > 1 %}
Команды для Куратора
{% endif %}
{% endif %}
{% if parent_id %}
{% if count_roles > 1 %}
Команды для Родителя
{% endif %}
{% endif %}
{% if student_id %}
{% if count_roles > 1 %}
Команды для Студента
{% endif %}
{% endif %}

""")

def is_admin(data: Dict, widget: Whenable, manager: DialogManager):
    if data.get("admin_id"):
        return True

def is_teacher(data: Dict, widget: Whenable, manager: DialogManager):
    if data.get("teacher_id"):
        return True

def is_curator(data: Dict, widget: Whenable, manager: DialogManager):
    if data.get("curator_id"):
        return True

def is_parent(data: Dict, widget: Whenable, manager: DialogManager):
    if data.get("parent_id"):
        return True

def is_student(data: Dict, widget: Whenable, manager: DialogManager):
    if data.get("student_id"):
        return True

def is_multi_role(data: Dict, widget: Whenable, manager: DialogManager):
    if data.get("count_roles") > 1:
        return True


dialog = Dialog(
    Window(
        Const("Меню:"),
        Multi(
            Const("\n*Команды для Администратора*\n", when=is_multi_role),
            Const("🧮 Занятие:\n"),
            Const("_1. Создать занятие:\n/addLesson_"),
            Const("_2. Посмотреть занятия:\n/getLessons_"),
            Const("_3. Редактировать занятие:\neditLesson_"),
            Const("_4. Удалить занятие:\n/deleteLesson_"),
            Const("\n📚 Домашняя работа:\n"),
            Const("_1. Создать ДЗ:\naddHomework_"),
            Const("_2. Удалить ДЗ:\ndeleteHomework_"),
            Const("\n👨‍👩‍👧‍👦 Клиенты:\n"),
            Const("_1. Привязать родителя к ученику:\n/bound_"),
            Const("_2. Отвязать родителя от ученика:\n/unbound_"),
            Const("_3. Добавить ученика в группу:\n/inGroup_"),
            Const("_4. Удалить ученика из группу:\n/outGroup_"),
            when=is_admin
        ),
        Multi(
            Const("\n*Команды для Преподавателя*\n", when=is_multi_role),
            Const("🧮 Занятие:\n"),
            Const("_1. Начать занятие: /startLesson_"),
            Const("_2. Отменить начало занятия: /cancelLesson_"),
            Const("_3. Закончить занятие: /endLesson_"),
            when=is_teacher
        ),
        Multi(
            Const("\n*Команды для Куратора*\n", when=is_multi_role),
            when=is_curator
        ),
        Multi(
            Const("\n*Команды для Родителя*\n", when=is_multi_role),
            when=is_parent
        ),
        Multi(
            Const("\n*Команды для Студента*\n", when=is_multi_role),
            when=is_student
        ),
        parse_mode=ParseMode.MARKDOWN,
        state=MenuSG.menu,
        getter=getter_start_data
    ),
)

@dp.message_handler(Command(commands="menu"), IsRegistered())
async def menu(message: Message, dialog_manager: DialogManager):
    data = await getter_start_data(dialog_manager)
    await dialog_manager.start(MenuSG.menu, data=data, mode=StartMode.RESET_STACK)
    await dialog_manager.done()

registry.register(dialog)