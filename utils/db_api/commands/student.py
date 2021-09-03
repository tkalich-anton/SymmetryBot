import logging
from typing import Union, List

import bson
import pymongo
from bson import ObjectId

from utils.db_api.commands.role import get_role_by_role_id
from utils.db_api.database import db
from utils.db_api.models import Student, User

async def get_student(
        user_id: ObjectId = None,
        student_id: ObjectId = None,
        telegram_id: int = None
) -> Union[Student, None]:
    """
    Получаем объект Student по переданному параметру.

    """
    if user_id is not None:
        request = await db.students.find_one({"account": user_id})
    elif student_id is not None:
        request = await db.students.find_one({"_id": student_id})
    elif telegram_id is not None:
        request = await db.students.find_one({"telegram_id": int(telegram_id)})
    else:
        logging.error("Ошбика: Ни одного аргумента не передано в функцию.")
        return
    if not request:
        return
    try:
        student = Student.build_from_mongo(request)
        return student
    except Exception as exc:
        logging.error("Ошбика: %s" % exc)
        return

async def get_students(
        group_id: ObjectId = None,
        parent_id: str = None,
        group_exist: bool = None,
        parent_exist: bool = None,
        sorting: str = "full_name",
        sort_direction=pymongo.ASCENDING
) -> List[Student]:
    """
    Получаем объекты Student по заданным параметрам.

    """
    students = []
    request_body = {}
    if group_exist == False:
        request_body["groups"] = {"$type": 10}
    elif group_exist == True:
        request_body["groups"] = {"$type": "objectId"}
    if group_id is not None:
        request_body["groups"] = {"$eq": group_id}
    if parent_exist == False:
        request_body["parent"] = {"$type": 10}
    if parent_exist == True:
        request_body["parent"] = {"$type": "objectId"}
    if parent_id is not None:
        request_body["parent"] = {"$eq": ObjectId(parent_id)}
    try:
        request = db.students.find(request_body).sort(sorting, sort_direction)
        async for document in request:
            student = Student.build_from_mongo(document)
            students.append(student)
    except Exception as exc:
        logging.error("Ошибка: %s" % exc)
    finally:
        return students
