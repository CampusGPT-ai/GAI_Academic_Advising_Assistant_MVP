from mongoengine import *
from institution.institution import Institution


class Profile(Document):
    _auto_id_field = 'id'
    user_id = StringField(required=True, unique=True)
    institution = ReferenceField(Institution, required=True)
    full_name = StringField(max_length=120)
    avatar = StringField()
    interests = ListField(StringField())
    demographics = DictField()
    academics = DictField()
    courses = ListField(StringField())
