import logging
from typing import List, Union

import pymongo
from bson import ObjectId

from utils.db_api.commands.role import get_role_by_role_id
from utils.db_api.database import db
from utils.db_api.models import Parent, Student, User

async def get_parent(
        user_id: ObjectId = None,
        parent_id: ObjectId = None,
        telegram_id: int = None
) -> Union[Parent, None]:
    """
    Получаем объект Parent по переданному параметру.

    """
    if user_id is not None:
        request = await db.parents.find_one({"account": user_id})
    elif parent_id is not None:
        request = await db.parents.find_one({"_id": parent_id})
    elif telegram_id is not None:
        request = await db.parents.find_one({"telegram_id": int(telegram_id)})
    else:
        logging.error("Ошбика: Ни одного аргумента не передано в функцию.")
        return
    if not request:
        return
    try:
        parent = Parent.build_from_mongo(request)
        return parent
    except Exception as exc:
        logging.error("Ошбика: %s" % exc)
        return

## Переделать!

async def get_parent_by_student(student: Student) -> Parent:
    """
    Получаем объект Parent по объекту Student

    """
    parent = await student.parent.fetch()
    if parent:
        return parent
    raise ValueError("К студенту не припязан родитель.")

## Переделать!

async def get_students_by_parent(parent: Parent) -> List[Union[dict[Student], None]]:
    """
    Получаем список объектов Student (детей родителя) по объекту Parent

    """
    result = []
    request = db.students.find({"parent": parent.id})
    async for student in request:
        result.append(student)
    return result

async def get_parents(
        confirmed: str = "0",
        sorting: str = "full_name",
        sort_direction=pymongo.ASCENDING
) -> List[Student]:
    """
    Получаем объекты Parents по заданным параметрам.

    """
    parents = []
    request_body = {}
    if not confirmed == "0" and isinstance(confirmed, bool):
        request_body["confirmed"] = confirmed
    try:
        request = db.parents.find(request_body).sort(sorting, sort_direction)
        async for document in request:
            parent = Student.build_from_mongo(document)
            parents.append(parent)
    except Exception as exc:
        logging.error("Ошибка: %s" % exc)
    finally:
        return parents
