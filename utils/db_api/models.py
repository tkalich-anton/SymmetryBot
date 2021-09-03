from umongo import Document, fields
from umongo.frameworks import MotorAsyncIOInstance

from utils.db_api.database import db

instance = MotorAsyncIOInstance(db)

@instance.register
class Role(Document):
    name = fields.StrField()
    type = fields.StrField()

    class Meta:
        collection_name = "users-permissions_role"
        strict = False

@instance.register
class Group(Document):
    group_number = fields.IntField()
    grade_number = fields.IntField()

    class Meta:
        collection_name = "groups"
        strict = False

@instance.register
class Teacher(Document):
    full_name = fields.StrField()
    telegram_id = fields.IntField()
    account = fields.ObjectIdField()

    class Meta:
        collection_name = "teachers"
        strict = False

@instance.register
class Curator(Document):
    full_name = fields.StrField()
    telegram_id = fields.IntField()
    account = fields.ObjectIdField()

    class Meta:
        collection_name = "curators"
        strict = False

@instance.register
class Parent(Document):
    full_name = fields.StrField()
    telegram_id = fields.IntField()
    account = fields.ObjectIdField()

    class Meta:
        collection_name = "parents"
        strict = False

@instance.register
class Student(Document):
    full_name = fields.StrField()
    telegram_id = fields.IntField()
    account = fields.ObjectIdField()
    groups = fields.ListField(fields.ReferenceField(Group, default=None))
    parent = fields.ReferenceField(Parent, default=None)

    class Meta:
        collection_name = "students"
        strict = False

@instance.register
class School(Document):
    groups = fields.ListField(fields.ReferenceField(Group))
    teachers = fields.ListField(fields.ReferenceField(Teacher))
    name = fields.StrField()

    class Meta:
        collection_name = "schools"
        strict = False

@instance.register
class Administrator(Document):
    full_name = fields.StrField()
    telegram_id = fields.IntField()
    account = fields.ObjectIdField()
    schools = fields.ListField(fields.ReferenceField(School))

    class Meta:
        collection_name = "administrators"
        strict = False

@instance.register
class Lesson(Document):
    status = fields.StrField()
    code = fields.StrField()
    title = fields.StrField()
    start = fields.DateTimeField()
    group = fields.ReferenceField(Group)
    school = fields.ReferenceField(School)
    teacher = fields.ReferenceField(Teacher)
    in_time = fields.ListField(fields.ReferenceField(Student))
    late = fields.ListField(fields.ReferenceField(Student))
    started_at = fields.DateTimeField()
    ended_at = fields.DateTimeField()

    class Meta:
        collection_name = "lessons"
        strict = False

@instance.register
class User(Document):
    full_name = fields.StrField()
    first_name = fields.StrField()
    last_name = fields.StrField()
    email = fields.StrField()
    username = fields.StrField()
    role = fields.ReferenceField(Role)
    teacher = fields.ReferenceField(Teacher, default=None)
    curator = fields.ReferenceField(Curator, default=None)
    student = fields.ReferenceField(Student, default=None)
    parent = fields.ReferenceField(Parent, default=None)
    administrator = fields.ReferenceField(Administrator, default=None)
    all_roles = fields.ListField(fields.ReferenceField(Role))
    password = fields.StrField()
    telegram_id = fields.IntField()
    confirmed = fields.BoolField()
    blocked = fields.BoolField()
    provider = fields.StrField()

    class Meta:
        collection_name = "users-permissions_user"
        strict = False

