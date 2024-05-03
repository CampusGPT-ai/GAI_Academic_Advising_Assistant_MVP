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

class Profile(Document):
    _auto_id_field = 'id'
    user_id = StringField(required=True, unique=True)
    first_name = StringField(required=False)
    active_conversation = ReferenceField('ConversationSimple', required=False)
    last_name = StringField(required=False)
    email = EmailField(required=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    considerations = ListField(DictField(required=False))
    meta = {
        'collection': 'user_profile',  # the name of your collection in the database
        'indexes': [
            'user_id'  # index this field for faster querying
        ]
    }

class kbDocument(Document):
    _auto_id_field = 'id'
    source = StringField(required=True)
    updated = StringField(required=True)
    text = StringField(required=True)
    meta = {
        'collection': 'kb_document',  # the name of your collection in the database
        'indexes': [
            'source'  # index this field for faster querying
        ]
    }

class catalogDocument(Document):
    _auto_id_field = 'id'
    source = StringField(required=True)
    updated = StringField(required=True)
    text = StringField(required=True)
    meta = {
        'collection': 'catalog_document',  # the name of your collection in the database
        'indexes': [
            'source'  # index this field for faster querying
        ]
    }

class Metadata(EmbeddedDocument):
    source = StringField(required=True)
    last_updated = StringField(required=True)  # Consider using DateTimeField for real datetime management
    title = StringField(required=True)

class WebPageDocument(Document):
    page_content = StringField(required=True)
    metadata = EmbeddedDocumentField(Metadata, required=True)
    type = StringField(required=True, default="Document")
    meta = {
        'collection': 'raw_webpage_document',  # the name of your collection in the database
    }


class indexDocument(Document):
    _auto_id_field = 'id'
    vector_id = StringField(required=True)
    source = StringField(required=True)
    last_updated = StringField(required=True)
    content = StringField(required=True)
    content_vector = ListField(FloatField())
    meta = {
        'collection': 'index_document',  # the name of your collection in the database
        'indexes': [
            'source'  # index this field for faster querying
        ]
    }

class indexCatalogDocument(Document):
    _auto_id_field = 'id'
    vector_id = StringField(required=True)
    source = StringField(required=True)
    last_updated = StringField(required=True)
    content = StringField(required=True)
    content_vector = ListField(FloatField())
    meta = {
        'collection': 'index_catalog_document',  # the name of your collection in the database
        'indexes': [
            'source'  # index this field for faster querying
        ]
    }

class Citation(EmbeddedDocument):
    citation_text = StringField(required=True)
    citation_path = StringField(required=True)

class MessageContent(EmbeddedDocument):
    role = StringField(required=True)
    message = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    keywords = StringField(required=False)
    rag_results = StringField(required=False)

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
    citations = ListField(EmbeddedDocumentField(Citation))
    follow_up_questions = ListField(StringField())


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


class ConversationSimple(Document):
    _auto_id_field = 'id'
    user_id = StringField(required=True)
    topic = StringField()
    start_time  = DateTimeField(required=True, default=datetime.now())
    end_time = DateTimeField()
    history = ListField(ReferenceField(RawChatMessage, required=False))
    meta = {'collection': 'conversations_simple'}

    def is_new(self):
        return self.end_time is None

    def end_conversation(self):
        self.end_time = datetime.now()
        self.save()