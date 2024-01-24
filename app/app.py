import openai, os
import mimetypes

from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
from sse_starlette.sse import EventSourceResponse
from mongoengine import connect, disconnect
from contextlib import asynccontextmanager
from functools import lru_cache
from cloud_services.gpt_models import AILLMModels, get_llm_model
from cloud_services.vector_search import VectorSearchService, get_search_client
from conversation.user_conversation import UserConversation
from azure.identity import DefaultAzureCredential
from data.models import Topic, Conversation, ConversationRequest, ChatMessage, Institution
from settings.settings import Settings
from util.json_helper import response_from_string
from util.logger_format import CustomFormatter
from azure.storage.blob.aio import BlobServiceClient
from fastapi.middleware.cors import CORSMiddleware
import logging, sys

credential = DefaultAzureCredential()
TOKEN = credential.get_token("https://cognitiveservices.azure.com/.default").token
openai.api_key = TOKEN
openai.api_type = os.getenv("OPENAI_API_TYPE")


load_dotenv()
ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.handlers.clear()  
logger.addHandler(ch)  



#logger.info(f"Loaded environment variables: {os.environ}")

@lru_cache()
def get_settings():
    return Settings()

# setting up mongo and openai as persistent connections
# will span the life of the app as deployed
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup block
    settings = get_settings()
    app.state.settings = settings
    logger.info(f"got settings from settings.py {settings.model_dump()}")
    # setup mongo connection
    db_name = settings.MONGO_DB
    db_conn = settings.MONGO_CONN_STR
    _mongo_conn = connect(db=db_name, host=db_conn)

    # setup openai connection
    openai.api_key = settings.AZURE_OPENAI_API_KEY
    openai.api_version = settings.OPENAI_API_VERSION
    openai.api_type = settings.OPENAI_API_TYPE

    # setup blob storage connection
    blob_client = BlobServiceClient(
        account_url=f"https://{settings.AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
        credential=settings.AZURE_STORAGE_ACCOUNT_CRED,
    )
    app.state.blob_container_client = blob_client.get_container_client(
        settings.AZURE_STORAGE_CONTAINER)
    

    yield

    # shutdown block
    disconnect()


app = FastAPI(lifespan=lifespan)

#TODO: need to figure out what origins to allow once we deploy
origins = [
    "http://localhost:3000",
    "http://localhost:5000",
    "http://localhost:5001",
    "localhost:3000",
    f"https://node{os.getenv('APP_NAME')}-development.azurewebsites.net",
    f"https://node{os.getenv('APP_NAME')}.azurewebsites.net"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/content/{path}")
async def get_content(path):
    # TODO: this is just a placeholder for now

    blob_container_client = app.state.blob_container_client
    blob = await blob_container_client.get_blob_client(path).download_blob()
    if not blob.properties or not blob.properties.has_key("content_settings"):
        raise HTTPException(status_code=404, detail="File not found")
    mime_type = blob.properties["content_settings"]["content_type"]
    if mime_type == "application/octet-stream":
        mime_type = mimetypes.guess_type(path)[0] or "application/octet-stream"

    return StreamingResponse(blob.chunks(), media_type=mime_type)

# anonoymous chat is used when the user is not logged in
@app.get("/chat/{user_question}")
async def chat_anonymous(
    user_question,
    ai_model: AILLMModels = Depends(
        lambda: get_llm_model(
            openai.api_type,
            app.state.settings.DEPLOYMENT_NAME or os.getenv("DEPLOYMENT_NAME"),
            app.state.settings.MODEL_NAME or os.getenv("MODEL_NAME"),
            app.state.settings.EMBEDDING or os.getenv("MODEL_NAME"),
        )
    ),
    search_client: VectorSearchService = Depends(
        lambda: get_search_client(
            app.state.settings.SEARCH_ENDPOINT or os.getenv("SEARCH_ENDPOINT"),
            app.state.settings.SEARCH_API_KEY or os.getenv("SEARCH_API_KEY"),
            app.state.settings.SEARCH_INDEX_NAME or os.getenv("SEARCH_INDEX_NAME"),
        )
    ),
):
    conversation = Conversation()
    #conversation.save()
    chain = UserConversation(
        conversation=conversation,
        ai_model=ai_model,
        search_client=search_client,
        sourcepage_field=app.state.settings.KB_FIELDS_SOURCEPAGE or os.getenv("KB_FIELDS_SOURCEPAGE"),
        content_field=app.state.settings.KB_FIELDS_CONTENT or os.getenv("KB_FIELDS_CONTENT"),
        settings=app.state.settings,
    )
    try:
        generator = chain.send_message(user_question)
        return EventSourceResponse(generator, media_type="text/event-stream")

    except Exception as e:
        logger.error(f"error getting response from gpt: {e.__str__} for {chain.ai_model}")
        return EventSourceResponse("unable to get response from gpt.  check logs", media_type="text/event-stream")

@app.get("/institutions/{institution_id}/users/{user_id}/chat/{user_question}")
async def create_conversation(
    institution_id,
    user_id,
    user_question,
    ai_model: AILLMModels = Depends(
        lambda: get_llm_model(
            openai.api_type,
            app.state.settings.DEPLOYMENT_NAME or os.getenv("DEPLOYMENT_NAME"),
            app.state.settings.MODEL_NAME or os.getenv("MODEL_NAME"),
            app.state.settings.EMBEDDING or os.getenv("EMBEDDING"),
        )
    ),
    search_client: VectorSearchService = Depends(
        lambda: get_search_client(
            app.state.settings.SEARCH_ENDPOINT or os.getenv("SEARCH_ENDPOINT"),
            app.state.settings.SEARCH_API_KEY or os.getenv("SEARCH_API_KEY"),
            app.state.settings.SEARCH_INDEX_NAME or os.getenv("SEARCH_INDEX_NAME")
        )
    ),
):

    logger.info(f"creating new conversation for user")

    conversation = Conversation(user=user)
    conversation.save()
    logger.info(f"created a new conversation with id: {conversation._auto_id_field}")
    
    chain = UserConversation(
        conversation=conversation,
        ai_model=ai_model,
        search_client=search_client,
        sourcepage_field=app.state.settings.KB_FIELDS_SOURCEPAGE or os.getenv("KB_FIELDS_SOURCEPAGE"),
        content_field=app.state.settings.KB_FIELDS_CONTENT or os.getenv("KB_FIELDS_CONTENT"),
        settings=app.state.settings,
    )
    
    generator = chain.send_message(user_question)
    return EventSourceResponse(generator, media_type="text/event-stream")

    

@app.get("/institutions/{institution_id}/users/{user_id}/conversations/{conversation_id}/chat/{user_question}")
async def chat(
    institution_id,
    user_id,
    conversation_id,
    user_question,
    ai_model: AILLMModels = Depends(
        lambda: get_llm_model(
            openai.api_type,
            app.state.settings.DEPLOYMENT_NAME or os.getenv("DEPLOYMENT_NAME"),
            app.state.settings.MODEL_NAME or os.getenv("MODEL_NAME"),
            app.state.settings.EMBEDDING or os.getenv("EMBEDDING"),
        )
    ),
    search_client: VectorSearchService = Depends(
        lambda: get_search_client(
            app.state.settings.SEARCH_ENDPOINT or os.getenv("SEARCH_ENDPOINT"),
            app.state.settings.SEARCH_API_KEY or os.getenv("SEARCH_API_KEY"),
            app.state.settings.SEARCH_INDEX_NAME or os.getenv("SEARCH_INDEX_NAME"),
        )
    ),
):
    logger.info("***********************starting chat message api")
 
    conversation = Conversation.objects(id=conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    else: 
        logger.info(f"got conversation {conversation} for user {user} and institution {inst}")

    chain = UserConversation(
        conversation=conversation,
        ai_model=ai_model,
        search_client=search_client,
        sourcepage_field=app.state.settings.KB_FIELDS_SOURCEPAGE or os.getenv("KB_FIELDS_SOURCEPAGE"),
        content_field=app.state.settings.KB_FIELDS_CONTENT or os.getenv("KB_FIELDS_CONTENT"),
        settings=app.state.settings,
    )
    generator = chain.send_message(user_question)
    return EventSourceResponse(generator, media_type="text/event-stream")


@app.get("/institutions")
async def get_institution():
    return Institution.objects().to_json()


@app.get("/institutions/{institution_id}/users")
async def get_profiles(institution_id):
    inst = Institution.objects(institution_id=institution_id).first()
    if inst is None:
        raise HTTPException(status_code=404, detail="Institution not found")

    return response_from_string(Profile.objects(institution=inst).to_json())


@app.get("/institutions/{institution_id}/topics")
async def get_topics(institution_id):
    inst = Institution.objects(institution_id=institution_id).first()
    if inst is None:
        raise HTTPException(status_code=404, detail="Institution not found")

    return response_from_string(Topic.objects(institution=inst).to_json())


@app.get("/institutions/{institution_id}/users/{user_id}/conversations")
async def get_conversations(institution_id, user_id):
    inst = Institution.objects(institution_id=institution_id).first()
    if inst is None:
        raise HTTPException(status_code=404, detail="Institution not found")

    user = Profile.objects(institution=inst, user_id=user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return response_from_string(Conversation.objects(user=user).to_json())


@app.get(
    "/institutions/{institution_id}/users/{user_id}/conversations/{conversation_id}/messages"
)
async def get_conversations(institution_id, user_id, conversation_id):
    inst = Institution.objects(institution_id=institution_id).first()
    if inst is None:
        raise HTTPException(status_code=404, detail="Institution not found")

    user = Profile.objects(institution=inst, user_id=user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    conversation = Conversation.objects(id=conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    logger.info(f"getting conversation for {user}, {conversation_id}: {conversation}")
    return response_from_string(
        ChatMessage.objects(user=user, conversation=conversation).to_json()
    )


@app.post("/institutions/{institution_id}/users/{user_id}/conversations")
async def start_conversation(institution_id, user_id, request: ConversationRequest):
    inst = Institution.objects(institution_id=institution_id).first()
    if inst is None:
        raise HTTPException(status_code=404, detail="Institution not found")

    user = Profile.objects(institution=inst, user_id=user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    conversation = Conversation(user=user, topic=request.topic)
    conversation.save()

    return response_from_string(conversation.to_json())


@app.get(
    "/institutions/{institution_id}/users/{user_id}/conversations/{conversation_id}/messages"
)
async def get_chat_messages(institution_id, user_id, conversation_id):
    inst = Institution.objects(institution_id=institution_id).first()
    if inst is None:
        raise HTTPException(status_code=404, detail="Institution not found")

    user = Profile.objects(institution=inst, user_id=user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    conversation = Conversation.objects(id=conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return response_from_string(
        ChatMessage.objects(conversation=conversation).to_json()
    )
