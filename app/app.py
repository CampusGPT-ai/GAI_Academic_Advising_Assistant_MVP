import openai, os, json
import contextvars
import uuid
import time

from typing import List
from dotenv import load_dotenv
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
from sse_starlette.sse import EventSourceResponse
from mongoengine import connect, disconnect
from contextlib import asynccontextmanager
from functools import lru_cache
from conversation.user_conversation import UserConversation
from conversation.ask_follow_up import FollowUp
from conversation.retrieve_messages import get_message_history
from azure.identity import DefaultAzureCredential
from data.models import Conversation, UserSession
from settings.settings import Settings

from azure.storage.blob.aio import BlobServiceClient
from fastapi.middleware.cors import CORSMiddleware
from app_auth import authorize_user
from app_auth.authorize_user import get_session_from_session

from user.get_user_info import UserInfo
import logging, sys
from conversation.retrieve_docs import SearchRetriever

load_dotenv()

logger = logging.getLogger(__name__)

request_id_contextvar = contextvars.ContextVar("request_id", default=None)
user_id_contextvar = contextvars.ContextVar("user_id", default=None)
session_id_contextvar = contextvars.ContextVar("session_id", default=None)


def get_context():
    return {
        "request_id": request_id_contextvar.get(),
        "session_id": session_id_contextvar.get(),
        "user_id": user_id_contextvar.get(),
    }


def set_context_from_session_data(session_data):
    user_id_contextvar.set(session_data.user_id)
    session_id_contextvar.set(session_data.session_id)


class ContextFilter(logging.Filter):
    def filter(self, record):
        ctx = get_context()
        record.request_id = ctx.get("request_id")
        record.session_id = ctx.get("session_id")
        record.user_id = ctx.get("user_id")
        record.code_version = os.getenv("GIT_SHA", "unknown")
        return True


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
        settings.AZURE_STORAGE_CONTAINER
    )

    yield

    # shutdown block
    disconnect()


from fastapi import Request
from fastapi.responses import JSONResponse


app = FastAPI(lifespan=lifespan)
app.include_router(authorize_user.router)


# TODO: need to figure out what origins to allow once we deploy
origins = [
    "http://localhost:3000",
    "http://localhost:5000",
    "http://localhost:5001",
    "localhost:3000",
    f"https://node{os.getenv('APP_NAME')}-development.azurewebsites.net",
    f"https://node{os.getenv('APP_NAME')}.azurewebsites.net",
    f"https://node{os.getenv('APP_NAME')}-dev-no-auth.azurewebsites.net",
    f"https://node{os.getenv('APP_NAME')}-development.azurewebsites.net/.auth/login/aad/callback",
    f"https://node{os.getenv('APP_NAME')}.azurewebsites.net/.auth/login/aad/callback"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["x-process-time"] = str(process_time)
    return response


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request_id_contextvar.set(request_id)
    request.headers.__dict__["_list"].append((b"x-request-id", request_id.encode()))
    try:
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response
    except Exception as e:
        logger.exception("Encountered exception: ")
        return JSONResponse(
            content={
                "message": "Request failed. Please try again.",
                "exception": str(e),
            },
            status_code=500,
        )
    finally:
        assert request_id_contextvar.get() == request_id


@app.middleware("http")
async def add_code_version(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-code-version"] = os.getenv("GIT_SHA", "unknown")
    return response


# all validations return 401 unauthorized if no user session.  {"detail":"Invalid or expired session"}
@app.get("/users/{session_guid}/questions")
async def get_sample_questions(
    session_data: UserSession = Depends(get_session_from_session),
):
    user = UserInfo(session_data)
    try:
        retriever: SearchRetriever = SearchRetriever.with_default_settings()
        data = retriever.generate_questions(user.get_user_info())
        return JSONResponse(content={"data": data}, status_code=200)
    except Exception as e:
        logger.error(
            f"failed to load sample questions with error {str(e)}",
        )
        return JSONResponse(
            content={"message": f"failed to load sample questions with error {str(e)}"},
            status_code=404,
        )

def get_conversation(conversation_id, session_data):
    try:
        if conversation_id == "0":
                logger.info(
                    "saving new conversation",
                )
                conversation = Conversation(user_id=session_data.user_id)
                conversation.save()
                logger.info(
                    f"got conversation information {conversation.id}",
                )
        else:
            conversation = Conversation.objects(id=conversation_id).first()
        if conversation is None:
            raise Exception("unable to create conversation for user chat.")
        return conversation
    except Exception as e:
        raise e

# regular chat - main API.  creates new conversation is conversation doesn't exist.
@app.get("/users/{session_guid}/conversations/{conversation_id}/chat/{user_question}")
async def chat(
    user_question,
    conversation_id,
    session_data: UserSession = Depends(get_session_from_session),
):
    set_context_from_session_data(session_data)
    try:
        logger.info(
            f"got data from api call: {user_question}, {conversation_id}",
        )
        conversation = get_conversation(conversation_id, session_data)

        chain = UserConversation.with_default_settings(
            session_data,
            conversation,
            model_num="GPT4",
        )
        generator = chain.send_message(user_question, conversation)
        return EventSourceResponse(generator, media_type="text/event-stream")
    except Exception as e:
        logger.error(
            f"Conversation not found with {str(e)}",
        )
        return JSONResponse(
            content={"message": f"Conversation not found with {str(e)}"},
            status_code=404,
        )

# regular chat - main API.  creates new conversation is conversation doesn't exist.
@app.get("/users/{session_guid}/conversations/{conversation_id}/chat_new/{user_question}")
async def chat_new(
    user_question,
    conversation_id,
    session_data: UserSession = Depends(get_session_from_session),
):
    set_context_from_session_data(session_data)
    try:
        logger.info(
            f"got data from api call: {user_question}, {conversation_id}",
        )
        conversation = get_conversation(conversation_id, session_data)
        chain = FollowUp(user_question,session_data,conversation)
    except Exception as e:
        logger.error(
            f"Conversation not found with {str(e)}",
        )
        return JSONResponse(
            content={"message": f"Conversation not found with {str(e)}"},
            status_code=404,
        )

# return list of user conversation ids
@app.get("/users/{session_guid}/conversations")
async def get_conversations(
    session_data: UserSession = Depends(get_session_from_session),
):
    set_context_from_session_data(session_data)
    try:
        logger.info(
            f"session info: {session_data.session_id}, {session_data.session_end}",
        )
        if "user_id" in session_data:
            logger.info(
                f"finding conversations for user: {session_data.user_id}",
            )
            conversations: List[Conversation] = Conversation.objects(
                user_id=session_data.user_id
            )
        if not conversations:
            logger.info("conversation not found in db")
            return Response(status_code=204)
        else:
            conversation_topics = []
            if conversations:
                for c in conversations:
                    c_dict = {
                        "topic": c.topic,
                        "id": str(c.id),
                        "start_time": (
                            c.start_time.isoformat() if c.start_time else None
                        ),
                        "end_time": c.end_time.isoformat() if c.end_time else None,
                    }
                    conversation_topics.append(c_dict)
            else:
                raise
            logger.info(
                f"got conversations from documents {conversation_topics}",
            )
            response = JSONResponse(
                jsonable_encoder(conversation_topics), status_code=200
            )
            logger.info(
                f"response serialized to json: ${response}",
            )
            return response
    except Exception as e:
        logger.error(
            f"failed to find conversation with error {str(e)}",
        )
        return JSONResponse(
            content={"message": f"failed to find conversation with error {str(e)}"},
            status_code=404,
        )


# return message history for a single conversation
@app.get("/users/{session_guid}/conversations/{conversation_id}/messages")
async def get_conversations(
    conversation_id, session_data: UserSession = Depends(get_session_from_session)
):
    set_context_from_session_data(session_data)
    try:
        conversation_dict = get_message_history(conversation_id)
        logger.debug(
            f"Getting conversation for {session_data.user_id}, {conversation_id}: {conversation_dict}",
        )
        return JSONResponse(content=conversation_dict, status_code=200)
    except Exception as e:
        logger.error(
            f"failed to find conversation with error {str(e)}",
        )
        return JSONResponse(
            content={"message": f"failed to get messages with error {str(e)}"},
            status_code=404,
        )
