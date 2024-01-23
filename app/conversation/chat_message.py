from datetime import datetime
from mongoengine import *
from pydantic import BaseModel
from app.backend.user_profile.profile_internal import Profile 
from conversation.conversation import Conversation

class Citation(EmbeddedDocument):
    citation_text = StringField(required=True)
    citation_path = StringField(required=True)


class ChatMessage(Document):
    _auto_id_field = 'id'
    user = ReferenceField(Profile)
    conversation = ReferenceField(Conversation, required=True)
    timestamp = DateTimeField(required=True, default=datetime.now())
    user_question = StringField()
    bot_response = StringField()
    citations = ListField(EmbeddedDocumentField('Citation'))
    follow_up_questions = ListField(StringField())


class ChatRequest(BaseModel):
    user_id: str | None = None
    institution_id: str | None = None
    conversation_id: str
    user_question: str