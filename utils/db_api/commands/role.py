from typing import Union

from bson import ObjectId

from utils.db_api.database import db
from utils.db_api.models import Role, User


async def get_role_by_role_id(role_id: str) -> Union[Role, None]:
    """
    Получаем объект Role по Role ID или None, если объект не найден.

    """
    try:
        requset = await db["users-permissions_role"].find_one({"_id": ObjectId(role_id)})
    except Exception as exc:
        print('Ошибка: %s' % exc)
        return
    if requset:
        role = Role.build_from_mongo(requset)
        return role
    raise ValueError("Роли с таким Role ID не существует.")


async def get_roles_by_user(user: User) -> list[dict]:
    """
    Получаем список объектов ролей пользователя

    """
    result = []
    for role_id in user.all_roles:
        try:
            role = await role_id.fetch()
            result.append(role)
        except Exception as exc:
            print('Ошибка: %s' % exc)
    return result


async def check_role(user: dict, check: str) -> Union[str, bool]:
    """
    Проверяем, обладает ли User данной ролью.

    Если User имеет данную роль, то возвращаем ID этой роли.

    Иначе возвращаем False.

    """
    if user["all_roles"]:
        for role_id in user["all_roles"]:
            role = await get_role_by_role_id(role_id)
            if role["type"] == check:
                try:
                    return user[check]
                except:
                    return False
    return False