import logging
from calendar import monthrange
from datetime import datetime

from bson import ObjectId
from dateutil.relativedelta import relativedelta

from aiogram_dialog import DialogManager

from utils.db_api.commands.lesson import get_lesson_by_code, get_lessons
from utils.db_api.commands.student import get_students
from utils.db_api.commands.teacher import get_teachers_by_school_id


async def getter_teachers_by_school_id(dialog_manager: DialogManager, **kwargs):
    try:
        teachers = await get_teachers_by_school_id(dialog_manager.current_context().dialog_data.get("school_id"))
        if teachers:
            teachers_list = []
            for teacher in teachers:
                # Помещаем в список кортежи (id, full_name)
                teachers_list.append((teacher.id, teacher.full_name))
            return {"teachers": teachers_list}
        else:
            return
    except Exception as exc:
        logging.error(exc)
        return

async def getter_lessons(dialog_manager: DialogManager, **kwargs):
    result = {}
    school_id = teacher_id = group_id = date_from = date_to = status = None
    lessons_list = []
    if dialog_manager.current_context().dialog_data.get("school_id"):
        school_id = dialog_manager.current_context().dialog_data["school_id"]
    if dialog_manager.current_context().dialog_data.get("teacher_id"):
        teacher_id = dialog_manager.current_context().dialog_data["teacher_id"]
    if dialog_manager.current_context().dialog_data.get("group_id"):
        group_id = dialog_manager.current_context().dialog_data["group_id"]
    if dialog_manager.current_context().dialog_data.get("lesson_status"):
        status = dialog_manager.current_context().dialog_data["lesson_status"]
    if dialog_manager.current_context().dialog_data.get("period"):
        if dialog_manager.current_context().dialog_data["period"] == "interval":
            date_from_string = f"{dialog_manager.current_context().dialog_data['date_from']} 00:00"
            date_to_string = f"{dialog_manager.current_context().dialog_data['date_to']} 23:59"
            date_from = datetime.strptime(date_from_string, "%Y-%m-%d %H:%M")
            date_to = datetime.strptime(date_to_string, "%Y-%m-%d %H:%M")
        elif dialog_manager.current_context().dialog_data["period"] == "current_week":
            now = datetime.now()
            day_number = now.weekday()
            date_from = now - relativedelta(days=day_number) - \
                relativedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
            date_to = now + relativedelta(days=(6 - day_number)) + \
                relativedelta(hours=(23 - now.hour), minutes=(59 - now.minute), seconds=(59 - now.second))
        elif dialog_manager.current_context().dialog_data["period"] == "next_week":
            now = datetime.now()
            day_number = now.weekday()
            date_from = now + relativedelta(weeks=1) - relativedelta(days=day_number) - \
                relativedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
            date_to = now + relativedelta(weeks=1) + relativedelta(days=(6 - day_number)) + \
                relativedelta(hours=(23 - now.hour), minutes=(59 - now.minute), seconds=(59 - now.second))
        elif dialog_manager.current_context().dialog_data["period"] == "current_month":
            now = datetime.now()
            number_of_days = monthrange(now.year, now.month)[1]
            date_from = now - relativedelta(days=(now.day - 1)) - \
                relativedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
            date_to = now + relativedelta(days=(number_of_days - now.day)) + \
                relativedelta(hours=(23 - now.hour), minutes=(59 - now.minute), seconds=(59 - now.second))
        elif dialog_manager.current_context().dialog_data["period"] == "next_month":
            now = datetime.now()
            next_month = now + relativedelta(months=1)
            number_of_days = monthrange(next_month.year, next_month.month)[1]
            date_from = next_month - relativedelta(days=(next_month.day - 1)) - \
                relativedelta(hours=next_month.hour, minutes=next_month.minute, seconds=next_month.second)
            date_to = next_month + relativedelta(days=(number_of_days - next_month.day)) + \
                relativedelta(
                    hours=(23 - next_month.hour),
                    minutes=(59 - next_month.minute),
                    seconds=(59 - next_month.second)
                )

    lessons = await get_lessons(date_from=date_from,
                                date_to=date_to,
                                school_id=school_id,
                                group_id=group_id,
                                teacher_id=teacher_id,
                                status=status)
    for lesson in lessons:
        group = await lesson.group.fetch()
        teacher = await lesson.teacher.fetch()
        lesson = {
            "code": lesson.code,
            "status": lesson.status,
            "teacher": teacher.full_name,
            "group": group.group_number,
            "date": lesson.start.strftime('%d.%m.%y'),
            "time": lesson.start.strftime('%H:%M'),
        }
        lessons_list.append(lesson)
    if date_from:
        result["date_from"] = date_from.strftime('%d.%m.%y')
    if date_to:
        result["date_to"] = date_to.strftime('%d.%m.%y')
    result["lessons"] = lessons_list
    return result


async def getter_lesson_by_lesson_code(dialog_manager: DialogManager, **kwargs):
    lesson_code = dialog_manager.current_context().dialog_data.get("lesson_code")
    lesson = await get_lesson_by_code(lesson_code)
    school = await lesson.school.fetch()
    group = await lesson.group.fetch()
    teacher = await lesson.teacher.fetch()
    students = await get_students(group_id=ObjectId(group.id))
    return {
        "status": lesson.status,
        "code": lesson.code,
        "title": lesson.title,
        "date": lesson.start.strftime('%d.%m.%y'),
        "time": lesson.start.strftime('%H:%M'),
        "group": group.group_number,
        "school": school.name,
        "teacher": teacher.full_name,
        "students": [{"full_name": student.full_name, "telegram_id": student.telegram_id} for student in students],
    }
