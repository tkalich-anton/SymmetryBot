import logging
from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def generate_reply_markup(*args):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    buttons = [x for x in args]
    keyboard.add(*buttons)
    return keyboard


def generate_inline_keyboard(buttons: List[dict[str: str]], last_button: InlineKeyboardButton = None, row_width=1):
    inline_keyboard = []
    inline_row = []
    count = 0
    url = login_url = callback_data = switch_inline_query = \
        switch_inline_query_current_chat = callback_game = pay = None
    for button in buttons:
        if "url" in button:
            url = button["url"]
        if "login_url" in button:
            login_url = button["login_url"]
        if "callback_data" in button:
            callback_data = button["callback_data"]
        if "switch_inline_query" in button:
            switch_inline_query = button["switch_inline_query"]
        if "switch_inline_query_current_chat" in button:
            switch_inline_query_current_chat = button["switch_inline_query_current_chat"]
        if "callback_game" in button:
            callback_game = button["callback_game"]
        if "pay" in button:
            pay = button["pay"]
        if url == login_url == callback_data == switch_inline_query == \
                switch_inline_query_current_chat == callback_game == pay is None:
            logging.error("Невозможно создать кнопку без второго аргумента!")
        elif "text" not in button:
            logging.error("Невозможно создать кнопку без текста!")
        else:
            count += 1
            text = button["text"]
            inline_button = InlineKeyboardButton(
                text=text,
                url=url,
                login_url=login_url,
                callback_data=callback_data,
                switch_inline_query=switch_inline_query,
                switch_inline_query_current_chat=switch_inline_query_current_chat,
                callback_game=callback_game,
                pay=pay,
            )
            inline_row.append(inline_button)
            if count % row_width == 0:
                inline_keyboard.append(inline_row)
                inline_row = []
    if last_button:
        inline_keyboard.append([last_button])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
