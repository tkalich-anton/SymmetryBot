import logging
from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

def role_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text="🙆‍♂️Ученик",
            callback_data="student"
        ),
        InlineKeyboardButton(
            text="💆‍♂️Родитель",
            callback_data="parent"
        )
    )
    markup.row(
        InlineKeyboardButton(
                text="👨‍💼Преподаватель",
                callback_data="teacher"
        ),
        InlineKeyboardButton(
                text="👨‍🚒Куратор",
                callback_data="curator"
        )
    )
    markup.row(
        InlineKeyboardButton(
                text="Назад",
                callback_data="to_wait_last_name"
        )
    )
    return markup
