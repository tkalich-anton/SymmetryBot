from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from aiogram_dialog import DialogRegistry

from data import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MongoStorage(uri=config.MONGO_URI)
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)
