from typing import Union

from bson import ObjectId

from utils.db_api.commands.role import get_role_by_role_id
from utils.db_api.database import db
from utils.db_api.models import User, Curator


async def get_curator_by_curator_id(curator_id: str) -> dict:
    """
    Получаем словарь объекта Curator по Administrator ID

    """
    curator = await db.curators.find_one({"_id": ObjectId(curator_id)})
    if curator:
        return curator
    ValueError("Не удалось найти Curator по указанному Curator ID")

async def get_curator_by_user_id(user_id: dict) -> dict:
    """
    Получаем словарь объекта Curator по User ID

    """
    curator_id = await is_curator(user_id)
    if curator_id:
        curator = await get_curator_by_curator_id(curator_id)
        if curator:
            return curator
        raise ValueError("Не удалось найти Curator по указанному User ID")
    raise ValueError("User не имеет роль Curator")


async def is_curator(user: dict) -> Union[str, bool]:
    """
    Проверяем, обладает ли User ролью Curator.

    Если User имеет роль Curator, то возвращаем Curator ID.

    Иначе возвращаем False.

    """
    for role_id in user["all_roles"]:
        role = await get_role_by_role_id(role_id)
        if role["type"] == "curator":
            return user["curator"] if user["curator"] else False
    return False
