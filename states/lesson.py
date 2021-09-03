from aiogram.dispatcher.filters.state import StatesGroup, State


class AddLessonSG(StatesGroup):
    school = State()
    group = State()
    teacher = State()
    date = State()
    time = State()
    title = State()
    confirm = State()

class GetLessonSG(StatesGroup):
    school = State()
    period = State()
    from_date = State()
    date_from = State()
    date_to = State()
    get_lessons = State()

class DeleteLessonSG(StatesGroup):
    code = State()
    confirm = State()

class StartLessonSG(StatesGroup):
    school = State()
    group = State()
    lesson = State()
    students = State()
    confirm = State()
