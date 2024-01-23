from datetime import datetime
from mongoengine import *
from app.backend.user_profile.profile_internal import Profile
from pydantic import BaseModel

# Mongo model
class Conversation(Document):
    _auto_id_field = 'id'
    user = ReferenceField(Profile)
    topic = StringField()
    start_time  = DateTimeField(required=True, default=datetime.now())
    end_time = DateTimeField()

def is_new(self):
    return self.end_time is None

def end_conversation(self):
    self.end_time = datetime.now()
    self.save()



# API model
class ConversationRequest(BaseModel):
    topic: str
    user_id: str | None = None
    institution_id: str | None = None
