import logging
from typing import Union

from bson import ObjectId

from utils.db_api.database import db
from utils.db_api.models import User, Teacher, School


async def get_teachers_by_school_id(school_id: str) -> list[Teacher]:
    result = []
    try:
        request = await db.schools.find_one({"_id": ObjectId(school_id)})
        if request is None:
            raise ValueError("School с таким School ID не найдена")
        school = School.build_from_mongo(request)
        for teacher in school.teachers:
            result.append(await teacher.fetch())
        return result
    except Exception as exc:
        logging.error('Ошибка: %s' % exc)

async def get_teacher(
        user_id: ObjectId = None,
        teacher_id: ObjectId = None,
        telegram_id: int = None
) -> Union[Teacher, None]:
    """
    Получаем объект Teacher по переданному параметру.

    """
    if user_id is not None:
        request = await db.teachers.find_one({"account": user_id})
    elif teacher_id is not None:
        request = await db.teachers.find_one({"_id": teacher_id})
    elif telegram_id is not None:
        request = await db.teachers.find_one({"telegram_id": int(telegram_id)})
    else:
        logging.error("Ошбика: Ни одного аргумента не передано в функцию.")
        return
    if not request:
        return
    try:
        teacher = Teacher.build_from_mongo(request)
        return teacher
    except Exception as exc:
        logging.error("Ошбика: %s" % exc)
        return