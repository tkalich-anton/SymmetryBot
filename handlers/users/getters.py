import logging
from typing import Union

from aiogram_dialog import DialogManager

from utils.db_api.commands.administrator import get_admin_by_admin_id
from utils.db_api.commands.school import get_school, get_schools
from utils.db_api.commands.teacher import get_teacher
from utils.db_api.commands.user import get_user


async def getter_start_data(dialog_manager: DialogManager, extra_data: dict = None, **kwargs) -> Union[dict, None]:
    result = {}
    try:
        user = await get_user(telegram_id=dialog_manager.event["from"]["id"])
        if user.administrator:
            result["admin_id"] = user.administrator.pk
        if user.teacher:
            result["teacher_id"] = user.teacher.pk
        if user.curator:
            result["curator_id"] = user.curator.pk
        if user.parent:
            result["parent_id"] = user.parent.pk
        if user.student:
            result["student_id"] = user.student.pk
        result["count_roles"] = len(user.all_roles)
        if extra_data:
            for key in extra_data:
                result[key] = extra_data[key]
        return result
    except Exception as exc:
        logging.error(exc)
        return

async def getter_schools_by_teacher_id(dialog_manager: DialogManager, **kwargs):
    schools_list = []
    if dialog_manager.current_context().start_data.get("teacher_id"):
        teacher_id = dialog_manager.current_context().start_data.get("teacher_id")
        try:
            schools = await get_schools(teacher_id=teacher_id)
            for school in schools:
                schools_list.append((school.id, school.name))
            return {"schools": schools_list}
        except Exception as exc:
            logging.error(exc)
            return


async def getter_schools_by_admin_id(dialog_manager: DialogManager, **kwargs):
    try:
        admin = await get_admin_by_admin_id(dialog_manager.current_context().start_data.get("admin_id"))
        schools_list = []
        for child in admin.schools:
            school = await child.fetch()
            if school:
                # Помещаем в список кортежи (id, title)
                schools_list.append((school.id, school.name))
        return {"schools": schools_list}
    except Exception as exc:
        logging.error(exc)
        return


async def getter_groups_by_school_id(dialog_manager: DialogManager, **kwargs):
    try:
        school = await get_school(dialog_manager.current_context().dialog_data.get("school_id"))
        if school:
            groups_list = []
            for child in school.groups:
                group = await child.fetch()
                if group:
                    # Помещаем в список кортежи (id, group_number)
                    groups_list.append((group.id, group.group_number))
            return {"groups": groups_list}
        else:
            logging.error("Школа с таким ID не найдена")
            return
    except Exception as exc:
        logging.error(exc)
        return