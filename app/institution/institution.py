from mongoengine import *


class Institution(Document):
    _auto_id_field = "id"
    institution_id = StringField(required=True, unique=True)
    name = StringField(required=True)
    website = StringField()
    logo = StringField()