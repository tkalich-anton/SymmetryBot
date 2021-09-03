from aiogram.utils.callback_data import CallbackData

create_lesson_cd = CallbackData("create_lesson", "group", "date", "teacher", "title")


def make_create_lesson_cd(group="0", date="0", teacher="0", title="0"):
    return create_lesson_cd.new(group=group, date=date, teacher=teacher, title=title)


inline_command_callback = CallbackData("simple_callback", "reply", "command_message_id")
