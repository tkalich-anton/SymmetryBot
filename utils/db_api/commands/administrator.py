import logging
from pprint import pprint
from typing import Union, List

from bson import ObjectId

from utils.db_api.commands.role import get_role_by_role_id
from utils.db_api.database import db
from utils.db_api.models import User, Administrator, School, Group

async def get_admin_by_admin_id(admin_id: str) -> Administrator:
    try:
        request = await db.administrators.find_one({"_id": ObjectId(admin_id)})
        if request is None:
            raise ValueError("Administrator с таким Administrator ID не найден")
        admin = Administrator.build_from_mongo(request)
        return admin
    except Exception as exc:
        logging.error('Ошибка: %s' % exc)


async def get_groups_by_admin(admin: Administrator) -> List[Group]:
    """
    Получаем все группы по Administrator.
    """
    result = []
    try:
        school = await admin.school.fetch()
        for group in school.groups:
            result.append(await group.fetch())
        return result
    except Exception as exc:
        logging.error('Ошибка: %s' % exc)
