from mongoengine import *
from institution.institution import Institution

class Topic(Document):
    _auto_id_field = 'id'
    institution = ReferenceField(Institution, required=True)
    topic = StringField(required=True)
    question = StringField()
    answer = StringField()
    related_interests = StringField()