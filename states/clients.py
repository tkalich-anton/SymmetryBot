from aiogram.dispatcher.filters.state import StatesGroup, State

class BoundSG(StatesGroup):
    student = State()
    parent = State()
    confirm = State()

class UnboundSG(StatesGroup):
    student = State()
    confirm = State()

class InGroupSG(StatesGroup):
    student = State()
    school = State()
    group = State()
    confirm = State()

class OutGroupSG(StatesGroup):
    school = State()
    group = State()
    student = State()
    confirm = State()




