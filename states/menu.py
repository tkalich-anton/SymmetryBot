from aiogram.dispatcher.filters.state import StatesGroup, State


class MenuSG(StatesGroup):
    menu = State()