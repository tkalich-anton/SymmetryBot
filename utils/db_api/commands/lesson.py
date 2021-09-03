import logging
from datetime import date
from typing import Union, List

from bson import ObjectId

from utils.db_api.database import db
from utils.db_api.models import Lesson


async def get_lesson_by_code(lesson_code: str) -> Union[Lesson, None]:
    """
    Получаем объект Lesson по Lesson Code или None, если объект не найден.

    """
    try:
        request = await db.lessons.find_one({"code": lesson_code})
        if request is None:
            logging.error("Занятие с таким кодом отсутствует")
            return
        lesson = Lesson.build_from_mongo(request)
        return lesson
    except Exception as exc:
        logging.error("Ошибка: %s" % exc)
        return


async def get_lessons(
        date_from: date = None,
        date_to: date = None,
        school_id: str = None,
        group_id: str = None,
        teacher_id: str = None,
        status: str = None,
        sorting: str = "start"
) -> List[Lesson]:
    """
    Получаем объекты Lesson по заданным параметрам.

    """
    lessons = []
    request_body = {}
    if date_from is not None and date_to is not None:
        request_body["start"] = {"$gte": date_from, "$lte": date_to}
    elif date_from is not None and date_to is None:
        request_body["start"] = {"$gte": date_from}
    elif date_from is None and date_to is not None:
        request_body["start"] = {"$lte": date_to}
    if school_id is not None:
        request_body["school"] = ObjectId(school_id)
    if group_id is not None:
        request_body["group"] = ObjectId(group_id)
    if teacher_id is not None:
        request_body["teacher"] = ObjectId(teacher_id)
    if status is not None:
        request_body["status"] = status
    try:
        request = db.lessons.find(request_body).sort(sorting)
        if request:
            async for document in request:
                lesson = Lesson.build_from_mongo(document)
                lessons.append(lesson)
    except Exception as exc:
        logging.error("Ошибка: %s" % exc)
    finally:
        return lessons
