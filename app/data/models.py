from bson.objectid import ObjectId
from datetime import datetime, timedelta
from mongoengine import *
from pydantic import BaseModel, Field

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
    version = StringField(required=False)
    meta = {
        'collection': 'raw_webpage_document',  # the name of your collection in the database
    }

class WebPageDocumentNew(Document):
    source = StringField(required=True)
    last_modified = StringField(required=True) # metadata/jsonLd/0/@graph/0/dateModified
    metadata_description = StringField(required=False) # metadata/jsonLd/0/@graph/0/description
    metadata_keywords = StringField(required=False)
    page_content = StringField(required=True)
    days_since_modified = IntField(required=False)
    word_count = IntField(required=False)
    sentence_count = IntField(required=False)
    char_count = IntField(required=False)
    average_word_length = IntField(required=False)
    average_sentence_length = IntField(required=False)
    header_count = IntField(required=False)
    list_count = IntField(required=False)
    link_count = IntField(required=False)
    subdomain = StringField(required=False)
    first_path_item = StringField(required=False)
    second_path_item = StringField(required=False)
    link_depth = IntField(required=False)
    link_depth_class = IntField(required=False)
    age_class = IntField(required=False)
    sentence_count_class = IntField(required=False)
    meta = {
    'collection': 'raw_webpage_document_v2', # the name of your collection in the database
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
#etadata/author,metadata/canonicalUrl,metadata/description,metadata/headers/access-control-allow-origin,metadata/headers/cache-control,metadata/headers/connection,metadata/headers/content-encoding,metadata/headers/content-length,metadata/headers/content-security-policy,metadata/headers/content-type,metadata/headers/date,metadata/headers/etag,metadata/headers/expires,metadata/headers/last-modified,metadata/headers/link,metadata/headers/pragma,metadata/headers/referrer-policy,metadata/headers/server,metadata/headers/set-cookie,metadata/headers/strict-transport-security,metadata/headers/transfer-encoding,metadata/headers/vary,metadata/headers/x-firefox-spdy,metadata/jsonLd,metadata/jsonLd/0/@context,metadata/jsonLd/0/@graph/0/@id,metadata/jsonLd/0/@graph/0/@type,metadata/jsonLd/0/@graph/0/breadcrumb/@id,metadata/jsonLd/0/@graph/0/dateModified,metadata/jsonLd/0/@graph/0/datePublished,metadata/jsonLd/0/@graph/0/description,metadata/jsonLd/0/@graph/0/image/@id,metadata/jsonLd/0/@graph/0/inLanguage,metadata/jsonLd/0/@graph/0/isPartOf/@id,metadata/jsonLd/0/@graph/0/name,metadata/jsonLd/0/@graph/0/potentialAction/0/@type,metadata/jsonLd/0/@graph/0/potentialAction/0/query-input,metadata/jsonLd/0/@graph/0/potentialAction/0/target/0,metadata/jsonLd/0/@graph/0/potentialAction/0/target/@type,metadata/jsonLd/0/@graph/0/potentialAction/0/target/urlTemplate,metadata/jsonLd/0/@graph/0/primaryImageOfPage/@id,metadata/jsonLd/0/@graph/0/thumbnailUrl,metadata/jsonLd/0/@graph/0/url,metadata/jsonLd/0/@graph/1/@id,metadata/jsonLd/0/@graph/1/@type,metadata/jsonLd/0/@graph/1/caption,metadata/jsonLd/0/@graph/1/contentUrl,metadata/jsonLd/0/@graph/1/description,metadata/jsonLd/0/@graph/1/height,metadata/jsonLd/0/@graph/1/inLanguage,metadata/jsonLd/0/@graph/1/itemListElement/0/@type,metadata/jsonLd/0/@graph/1/itemListElement/0/item,metadata/jsonLd/0/@graph/1/itemListElement/0/name,metadata/jsonLd/0/@graph/1/itemListElement/0/position,metadata/jsonLd/0/@graph/1/itemListElement/1/@type,metadata/jsonLd/0/@graph/1/itemListElement/1/item,metadata/jsonLd/0/@graph/1/itemListElement/1/name,metadata/jsonLd/0/@graph/1/itemListElement/1/position,metadata/jsonLd/0/@graph/1/itemListElement/2/@type,metadata/jsonLd/0/@graph/1/itemListElement/2/name,metadata/jsonLd/0/@graph/1/itemListElement/2/position,metadata/jsonLd/0/@graph/1/name,metadata/jsonLd/0/@graph/1/potentialAction/0/@type,metadata/jsonLd/0/@graph/1/potentialAction/0/query-input,metadata/jsonLd/0/@graph/1/potentialAction/0/target/@type,metadata/jsonLd/0/@graph/1/potentialAction/0/target/urlTemplate,metadata/jsonLd/0/@graph/1/url,metadata/jsonLd/0/@graph/1/width,metadata/jsonLd/0/@graph/2/@id,metadata/jsonLd/0/@graph/2/@type,metadata/jsonLd/0/@graph/2/description,metadata/jsonLd/0/@graph/2/inLanguage,metadata/jsonLd/0/@graph/2/itemListElement/0/@type,metadata/jsonLd/0/@graph/2/itemListElement/0/item,metadata/jsonLd/0/@graph/2/itemListElement/0/name,metadata/jsonLd/0/@graph/2/itemListElement/0/position,metadata/jsonLd/0/@graph/2/itemListElement/1/@type,metadata/jsonLd/0/@graph/2/itemListElement/1/item,metadata/jsonLd/0/@graph/2/itemListElement/1/name,metadata/jsonLd/0/@graph/2/itemListElement/1/position,metadata/jsonLd/0/@graph/2/itemListElement/2/@type,metadata/jsonLd/0/@graph/2/itemListElement/2/name,metadata/jsonLd/0/@graph/2/itemListElement/2/position,metadata/jsonLd/0/@graph/2/name,metadata/jsonLd/0/@graph/2/potentialAction/0/@type,metadata/jsonLd/0/@graph/2/potentialAction/0/query-input,metadata/jsonLd/0/@graph/2/potentialAction/0/target/@type,metadata/jsonLd/0/@graph/2/potentialAction/0/target/urlTemplate,metadata/jsonLd/0/@graph/2/url,metadata/jsonLd/0/@graph/3/@id,metadata/jsonLd/0/@graph/3/@type,metadata/jsonLd/0/@graph/3/description,metadata/jsonLd/0/@graph/3/inLanguage,metadata/jsonLd/0/@graph/3/name,metadata/jsonLd/0/@graph/3/potentialAction/0/@type,metadata/jsonLd/0/@graph/3/potentialAction/0/query-input,metadata/jsonLd/0/@graph/3/potentialAction/0/target/@type,metadata/jsonLd/0/@graph/3/potentialAction/0/target/urlTemplate,metadata/jsonLd/0/@graph/3/url,metadata/keywords,metadata/languageCode,metadata/openGraph/0/content,metadata/openGraph/0/property,metadata/openGraph/1/content,metadata/openGraph/1/property,metadata/openGraph/2/content,metadata/openGraph/2/property,metadata/openGraph/3/content,metadata/openGraph/3/property,metadata/openGraph/4/content,metadata/openGraph/4/property,metadata/openGraph/5/content,metadata/openGraph/5/property,metadata/openGraph/6/content,metadata/openGraph/6/property,metadata/openGraph/7/content,metadata/openGraph/7/property,metadata/openGraph/8/content,metadata/openGraph/8/property,metadata/openGraph/9/content,metadata/openGraph/9/property,metadata/openGraph/10/content,metadata/openGraph/10/property,metadata/openGraph/11/content,metadata/openGraph/11/property,metadata/openGraph/12/content,metadata/openGraph/12/property,metadata/openGraph/13/content,metadata/openGraph/13/property,metadata/title,markdown,metadata/headers/service-worker-allowed,metadata/headers/x-aspnet-version,metadata/headers/x-powered-by,metadata/jsonLd/0/@graph/1/itemListElement/2/item,metadata/jsonLd/0/@graph/1/itemListElement/3/@type,metadata/jsonLd/0/@graph/1/itemListElement/3/name,metadata/jsonLd/0/@graph/1/itemListElement/3/position,metadata/headers/keep-alive,metadata/headers/x-pingback,metadata/headers/x-robots-tag,metadata/headers/x-ua-compatible,days_since_modified,word_count,sentence_count,char_count,average_word_length,average_sentence_length,header_count,list_count,link_count,sentence_count_class,age_class,subdomain,first_path_item,second_path_item,link_depth,link_depth_class
class indexDocumentv2(Document):
    vector_id = StringField(required=True)
    source = StringField(required=True)
    last_modified = StringField(required=True) # metadata/jsonLd/0/@graph/0/dateModified
    metadata_description = StringField(required=False) # metadata/jsonLd/0/@graph/0/description
    metadata_keywords = StringField(required=False)
    page_content = StringField(required=True)
    content_vector = ListField(FloatField())
    days_since_modified = IntField(required=False)
    word_count = IntField(required=False)
    sentence_count = IntField(required=False)
    char_count = IntField(required=False)
    average_word_length = IntField(required=False)
    average_sentence_length = IntField(required=False)
    header_count = IntField(required=False)
    list_count = IntField(required=False)
    link_count = IntField(required=False)
    subdomain = StringField(required=False)
    first_path_item = StringField(required=False)
    second_path_item = StringField(required=False)
    link_depth = IntField(required=False)
    link_depth_class = IntField(required=False)
    age_class = IntField(required=False)
    sentence_count_class = IntField(required=False)
    subdomain_vector=ListField(FloatField())
    first_path_vector=ListField(FloatField())
    second_path_vector=ListField(FloatField())
    meta = {
    'collection': 'index_document_v2', # the name of your collection in the database
    }


class Citation(EmbeddedDocument):
    citation_text = StringField(required=True)
    citation_path = StringField(required=True)

class MessageContent(EmbeddedDocument):
    _id = ObjectIdField(required=True, default=ObjectId )
    role = StringField(required=True)
    message = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    rag_results = StringField(required=False)
    feedback = DictField(required=False)

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

class Question(BaseModel):
    scale: int = Field(ge=1, le=5)

class Comment(BaseModel):
    comment: str

class Feedback(BaseModel):
    relevance : Question
    accuracy : Question
    usefulness : Question
    helpfulnessOfLinks : Question
    learnMoreOptions : Question
    comments : Comment
