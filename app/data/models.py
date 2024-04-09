from datetime import datetime, timedelta
from mongoengine import *
from pydantic import BaseModel

# Conversation > Chat Message > Raw Chat Message > Message Content 
# -------------------->Citation
#--------------------------------------->UserSession

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

class Citation(EmbeddedDocument):
    citation_text = StringField(required=False)
    citation_path = StringField(required=True)

class MessageContent(EmbeddedDocument):
    role = StringField(required=True)
    message = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)

class RawChatMessage(Document):
    _auto_id_field = 'id'
    # removing reference to profile, pending gather login
    # user = ReferenceField(Profile)
    user_session_id = ReferenceField('UserSession', required=True)
    message = ListField(EmbeddedDocumentField(MessageContent))
    meta = {
        'collection': 'raw_chat_message',  # the name of your collection in the database
        'indexes': [
            'user_session_id'  # index this field for faster querying
        ]
    } 

class ChatMessage(EmbeddedDocument):
    message = ReferenceField(RawChatMessage, required = True)
    citations = ListField(EmbeddedDocumentField(Citation), required = False)
    follow_up_questions = ListField(StringField(), required = False)


class Conversation(Document):
    topic = StringField()
    user_id = StringField()
    start_time  = DateTimeField(required=True, default=datetime.now())
    end_time = DateTimeField()
    messages = ListField(EmbeddedDocumentField(ChatMessage, required=False))
    meta = {'collection': 'conversations'}

    def is_new(self):
        return self.end_time is None

    def end_conversation(self):
        self.end_time = datetime.now()
        self.save()
