import logging
from typing import List

import pymongo
from bson import ObjectId

from utils.db_api.database import db
from utils.db_api.models import Group, School


async def get_group(group_id: str) -> Group:
    try:
        request = await db.groups.find_one({"_id": ObjectId(group_id)})
        if request is None:
            raise ValueError("Group с таким Group ID не найдена")
        group = Group.build_from_mongo(request)
        return group
    except Exception as exc:
        logging.error('Ошибка: %s' % exc)

async def get_school(school_id: str) -> School:
    try:
        request = await db.schools.find_one({"_id": ObjectId(school_id)})
        if request is None:
            raise ValueError("School с таким School ID не найдена")
        school = School.build_from_mongo(request)
        return school
    except Exception as exc:
        logging.error('Ошибка: %s' % exc)

async def get_schools(
        teacher_id: ObjectId = None,
        sorting: str = "name",
        sort_direction=pymongo.ASCENDING
) -> List[School]:
    schools = []
    request_body = {}
    if teacher_id is not None:
        request_body["teachers"] = {"$eq": teacher_id}
    try:
        request = db.schools.find(request_body).sort(sorting, sort_direction)
        if request is None:
            raise ValueError("School с таким School ID не найдена")
        async for document in request:
            school = School.build_from_mongo(document)
            schools.append(school)
        return schools
    except Exception as exc:
        logging.error('Ошибка: %s' % exc)