from aiogram import Dispatcher

from loader import dp
from .permission import CheckRole, IsUnregistered, IsRegistered

if __name__ == "filters":
    dp.filters_factory.bind(CheckRole)
    dp.filters_factory.bind(IsUnregistered)
    dp.filters_factory.bind(IsRegistered)
