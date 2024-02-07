import openai, os, json
from typing import List
from dotenv import load_dotenv
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
from sse_starlette.sse import EventSourceResponse
from mongoengine import connect, disconnect
from contextlib import asynccontextmanager
from functools import lru_cache
from conversation.user_conversation import UserConversation
from conversation.retrieve_messages import get_message_history
from azure.identity import DefaultAzureCredential
from data.models import Conversation, UserSession
from settings.settings import Settings

from util.logger_format import CustomFormatter
from azure.storage.blob.aio import BlobServiceClient
from fastapi.middleware.cors import CORSMiddleware
from app_auth import authorize_user
from app_auth.authorize_user import get_session_from_session

from user.get_user_info import UserInfo
import logging, sys
from conversation.retrieve_docs import SearchRetriever


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

from fastapi import Request
from fastapi.responses import JSONResponse


app = FastAPI(lifespan=lifespan)
app.include_router(authorize_user.router)



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

# all validations return 401 unauthorized if no user session.  {"detail":"Invalid or expired session"}
@app.get("/users/{session_guid}/questions")
async def get_sample_questions(session_data: UserSession = Depends(get_session_from_session)):
    user = UserInfo(session_data)
    retriever : SearchRetriever = SearchRetriever.with_default_settings()
    data = retriever.generate_questions(user.get_user_info())
    return JSONResponse(content={"data": data}, status_code=200)
   
# regular chat - main API.  creates new conversation is conversation doesn't exist.  
@app.get("/users/{session_guid}/conversations/{conversation_id}/chat/{user_question}")
async def chat(
    user_question, 
    conversation_id,
    session_data: UserSession = Depends(get_session_from_session)
): 
    try:
        logger.info(f'got data from api call: {user_question}, {conversation_id}')
        if conversation_id=='0':
            logger.info("saving new conversation")
            conversation = Conversation(user_id=session_data.user_id)
            conversation.save()
            logger.info(f'got conversation information {conversation.id}')
        else: 
            conversation = Conversation.objects(id=conversation_id).first()
        if conversation is None:
            return JSONResponse(content={"message": "Conversation not found"}, status_code=404)
        
        chain = UserConversation.with_default_settings(session_data, conversation, model_num='GPT4')
        generator = chain.send_message(user_question)
        return EventSourceResponse(generator, media_type="text/event-stream")
    except Exception as e:
        return JSONResponse(content={"message": "Conversation not found"}, status_code=404)

# return list of user conversation ids
@app.get("/users/{session_guid}/conversations")
async def get_conversations(session_data: UserSession = Depends(get_session_from_session)):
    try:
        logger.info(f"session info: {session_data.session_id}, {session_data.session_end}")
        if 'user_id' in session_data:
            logger.info(f"finding conversations for user: {session_data.user_id}")
            conversations : List[Conversation] = Conversation.objects(user_id=session_data.user_id)
        if not conversations:
            logger.error("conversation not found in db")
            return JSONResponse(content={"message": "Conversation not found"}, status_code=404)
        else:
            conversation_topics = []
            if conversations:
                for c in conversations:
                    c_dict = {
                        
                        "topic": c.topic,
                        "id": str(c.id),
                        "start_time": c.start_time.isoformat() if c.start_time else None,
                        "end_time": c.end_time.isoformat() if c.end_time else None,
                    }
                    conversation_topics.append(c_dict)
            else:
                raise
            logger.info(f"got conversations from documents {conversation_topics}")
            response = JSONResponse(jsonable_encoder(conversation_topics), status_code=200)
            logger.info(f"response serialized to json: ${response}")
            return response
    except Exception as e:
        logger.error(f"failed to find conversation with error {str(e)}")
        return JSONResponse(content={"message": f"failed to find conversation with error {str(e)}"}, status_code=404)

# return message history for a single conversation
@app.get(
    "/users/{session_guid}/conversations/{conversation_id}/messages"
)
async def get_conversations(conversation_id, session_data: UserSession = Depends(get_session_from_session)):
    try:
        conversation_dict = get_message_history(conversation_id)
        logger.info(f"Getting conversation for {session_data.user_id}, {conversation_id}: {conversation_dict}")
        return JSONResponse(content = conversation_dict, status_code = 200)
    except Exception as e:
        logger.error(f"failed to find conversation with error {str(e)}")
        return JSONResponse(content={"message": f"failed to get messages with error {str(e)}"}, status_code=404) 
