import motor.motor_asyncio

from data.config import MONGO_URI, DATABASE

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE]
