import logging

from aiogram_dialog import DialogManager

from utils.db_api.commands.parent import get_parents
from utils.db_api.commands.student import get_students, get_student

async def getter_students(dialog_manager: DialogManager, **kwargs):
    parent_exist = group_exist = group_id = None
    if dialog_manager.current_context().start_data.get("fs_parent_exist") is not None:
        parent_exist = dialog_manager.current_context().start_data.get("fs_parent_exist")
    if dialog_manager.current_context().start_data.get("fs_group_exist") is not None:
        group_exist = dialog_manager.current_context().start_data.get("fs_group_exist")
    if dialog_manager.current_context().dialog_data.get("group_id") is not None:
        group_id = dialog_manager.current_context().dialog_data.get("group_id")
    result = []
    try:
        students = await get_students(parent_exist=parent_exist, group_exist=group_exist, group_id=group_id)
        for student in students:
            result.append((student.telegram_id, student.full_name))
        return {"students": result}
    except Exception as exc:
        logging.error(exc)


async def getter_parents(dialog_manager: DialogManager, **kwargs):
    result = {}
    if dialog_manager.current_context().dialog_data.get("student_telegram_id") is not None:
        student_telegram_id = dialog_manager.current_context().dialog_data.get("student_telegram_id")
        student_full_name = dialog_manager.current_context().dialog_data.get("student_full_name")
        result["student"] = {
            "full_name": student_full_name,
            "telegram_id": student_telegram_id,
        }
    try:
        student_list = []
        parents = await get_parents()
        for parent in parents:
            student_list.append((parent.telegram_id, parent.full_name))
        result["parents"] = student_list
        return result
    except Exception as exc:
        logging.error(exc)

async def getter_final_data_bound(dialog_manager: DialogManager, **kwargs):
    student_full_name = dialog_manager.current_context().dialog_data.get("student_full_name")
    parent_full_name = dialog_manager.current_context().dialog_data.get("parent_full_name")
    student_telegram_id = dialog_manager.current_context().dialog_data.get("student_telegram_id")
    parent_telegram_id = dialog_manager.current_context().dialog_data.get("parent_telegram_id")
    return {
        "student_full_name": student_full_name,
        "student_telegram_id": student_telegram_id,
        "parent_full_name": parent_full_name,
        "parent_telegram_id": parent_telegram_id,
}

async def getter_final_data_unbound(dialog_manager: DialogManager, **kwargs):
    student_full_name = dialog_manager.current_context().dialog_data.get("student_full_name")
    student_telegram_id = dialog_manager.current_context().dialog_data.get("student_telegram_id")
    student = await get_student(telegram_id=student_telegram_id)
    parent = await student.parent.fetch()
    return {
        "student_full_name": student_full_name,
        "student_telegram_id": student_telegram_id,
        "parent_full_name": parent.full_name,
        "parent_telegram_id": parent.telegram_id,
    }

async def getter_final_data_io_group(dialog_manager: DialogManager, **kwargs):
    student_full_name = dialog_manager.current_context().dialog_data.get("student_full_name")
    student_telegram_id = dialog_manager.current_context().dialog_data.get("student_telegram_id")
    group_number = dialog_manager.current_context().dialog_data.get("group_number")
    return {
        "student_full_name": student_full_name,
        "student_telegram_id": student_telegram_id,
        "group_number": group_number
}