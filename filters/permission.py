import logging

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from loader import bot
from utils.db_api.commands.user import get_user
from utils.db_api.commands.role import get_roles_by_user


class CheckRole(BoundFilter):

    def __init__(self, role: str):
        self.role = role

    async def check(self, message: types.Message):
        user = await get_user(telegram_id=message.from_user.id)
        try:
            roles = await get_roles_by_user(user)
        except Exception as exc:
            print('Ошибка: %s' % exc)
            return
        for role in roles:
            if role["type"] == self.role:
                return True

class IsRegistered(BoundFilter):

    async def check(self, message: types.Message):
        user = await get_user(telegram_id=message.from_user.id)
        if user:
            return True

class IsUnregistered(BoundFilter):

    async def check(self, message: types.Message):
        user = await get_user(telegram_id=message.from_user.id)
        if not user:
            return True