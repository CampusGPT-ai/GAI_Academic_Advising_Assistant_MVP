from datetime import datetime, timedelta
from mongoengine import *
from pydantic import BaseModel

class Institution(Document):
    _auto_id_field = "id"
    institution_id = StringField(required=True, unique=True)
    name = StringField(required=True)
    website = StringField()
    logo = StringField()

class Conversation(Document):
    _auto_id_field = 'id'
    # removing reference to profile, pending gather login
    # user = ReferenceField(Profile)
    topic = StringField()
    start_time  = DateTimeField(required=True, default=datetime.now())
    end_time = DateTimeField()

    def is_new(self):
        return self.end_time is None

    def end_conversation(self):
        self.end_time = datetime.now()
        self.save()


class Citation(EmbeddedDocument):
    citation_text = StringField(required=True)
    citation_path = StringField(required=True)


class ChatMessage(Document):
    _auto_id_field = 'id'
    # removing reference to profile, pending gather login
    # user = ReferenceField(Profile)
    conversation = ReferenceField(Conversation, required=True)
    timestamp = DateTimeField(required=True, default=datetime.now())
    user_question = StringField()
    bot_response = StringField()
    citations = ListField(EmbeddedDocumentField('Citation'))
    follow_up_questions = ListField(StringField())

class Topic(Document):
    _auto_id_field = 'id'
    institution = ReferenceField(Institution, required=True)
    topic = StringField(required=True)
    question = StringField()
    answer = StringField()
    related_interests = StringField()

class ChatRequest(BaseModel):
    user_id: str | None = None
    institution_id: str | None = None
    conversation_id: str
    user_question: str

class ConversationRequest(BaseModel):
    topic: str
    user_id: str | None = None
    institution_id: str | None = None
    
class UserSession(Document):
    _auto_id_field = 'id'
    user_id = StringField(required=True, unique=False)
    session_id = StringField(required=True, unique=True)
    session_start = DateTimeField(required=True, default=datetime.now())
    session_end = DateTimeField(required=True, default=datetime.now())
    meta = {
        'collection': 'user_session',  # the name of your collection in the database
        'indexes': [
            'session_id'  # index this field for faster querying
        ]
    }

    
