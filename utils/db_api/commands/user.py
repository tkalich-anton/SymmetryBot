import logging
from typing import Union

from bson import ObjectId

from utils.db_api.database import db
from utils.db_api.models import User

async def get_user(
        user_id: ObjectId = None,
        telegram_id: int = None,
        username: str = None,
        administrator_id: ObjectId = None,
        teacher_id: ObjectId = None,
        curator_id: ObjectId = None,
        parent_id: ObjectId = None,
        student_id: ObjectId = None,
) -> Union[User, None]:
    """
    Получаем объект User по переданному параметру.

    """
    if user_id is not None:
        request = await db["users-permissions_user"].find_one({"_id": user_id})
    elif telegram_id is not None:
        request = await db["users-permissions_user"].find_one({"telegram_id": telegram_id})
    elif username is not None:
        request = await db["users-permissions_user"].find_one({"username": username})
    elif administrator_id is not None:
        request = await db["users-permissions_user"].find_one({"administrator": administrator_id})
    elif teacher_id is not None:
        request = await db["users-permissions_user"].find_one({"teacher": teacher_id})
    elif curator_id is not None:
        request = await db["users-permissions_user"].find_one({"curator": curator_id})
    elif parent_id is not None:
        request = await db["users-permissions_user"].find_one({"parent": parent_id})
    elif student_id is not None:
        request = await db["users-permissions_user"].find_one({"student": student_id})
    else:
        logging.error("Ошбика: Ни одного аргумента не передано в функцию.")
        return
    if not request:
        return
    try:
        user = User.build_from_mongo(request)
        return user
    except Exception as exc:
        logging.error("Ошбика: %s" % exc)
        return