from aiogram_dialog import DialogManager

from utils.db_api.commands.lesson import get_lesson_by_code
from utils.db_api.commands.school import get_group
from utils.db_api.commands.student import get_student
from utils.db_api.commands.teacher import get_teacher


async def getter_final_data_add_lesson(dialog_manager: DialogManager, **kwargs):
    teacher = await get_teacher(teacher_id=dialog_manager.current_context().dialog_data.get("teacher_id"))
    group = await get_group(dialog_manager.current_context().dialog_data.get("group_id"))
    return {
        "admin_id": dialog_manager.current_context().start_data.get("admin_id"),
        "school_id": dialog_manager.current_context().dialog_data.get("school_id"),
        "school_name": dialog_manager.current_context().dialog_data.get("school_name"),
        "group": group.group_number,
        "teacher": teacher.full_name,
        "year": dialog_manager.current_context().dialog_data.get("year"),
        "month": dialog_manager.current_context().dialog_data.get("month"),
        "day": dialog_manager.current_context().dialog_data.get("day"),
        "hour": dialog_manager.current_context().dialog_data.get("hour"),
        "minute": dialog_manager.current_context().dialog_data.get("minute"),
        "title": dialog_manager.current_context().dialog_data.get("title"),
    }

async def getter_final_data_start_lesson(dialog_manager: DialogManager, **kwargs):
    lesson_code = dialog_manager.current_context().dialog_data.get("lesson_code")
    lesson = await get_lesson_by_code(lesson_code)
    students = []
    for student_telegram_id in dialog_manager.current_context().widget_data.get("students"):
        student = await get_student(telegram_id=int(student_telegram_id))
        students.append({"telegram_id": student.telegram_id, "full_name": student.full_name})
    if lesson:
        lesson_theme = lesson.title
        return {
            "lesson_code": lesson_code,
            "lesson_theme": lesson_theme,
            "students": students,
        }