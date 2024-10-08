import openai, os, json
import contextvars
import uuid
import time

    
from conversation.retrieve_messages import get_history_as_messages, get_last_response
from conversation.retrieve_conversations import get_conversation, conversation_to_dict, get_all_conversations
from conversation.return_questions import get_questions
from typing import List
from dotenv import load_dotenv
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, BackgroundTasks
from mongoengine import connect, disconnect
from contextlib import asynccontextmanager
from functools import lru_cache
from conversation.answer_user_question import QnAResponse
from conversation.retrieve_messages import get_message_history,get_history_as_messages
from data.models import UserSession, Feedback
from settings.settings import Settings
from conversation.check_considerations import Considerations
from azure.storage.blob.aio import BlobServiceClient
from fastapi.middleware.cors import CORSMiddleware
from app_auth import authorize_user
from app_auth.authorize_user import get_session_from_session
from threading import Thread
from conversation.run_graph import GraphFinder
import logging
from conversation.update_conversation import update_conversation_history, update_conversation_history_with_feedback
from graph_update.graph_eval_and_update import NodeEditor
from data.models import ConversationSimple
from data.query_mongo import count_reviews,  load_data_to_dataframe
load_dotenv()

logger = logging.getLogger(__name__)
logging.getLogger('azure').setLevel(logging.WARNING)

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
    logger.debug(f"got settings from settings.py {settings.model_dump()}")
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
    "http://127.0.0.1:3000",
    "localhost:3000",
    f"https://node{os.getenv('APP_NAME')}-development.azurewebsites.net",
    f"https://node{os.getenv('APP_NAME')}.azurewebsites.net",
    f"https://node{os.getenv('APP_NAME')}-staging.azurewebsites.net",
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
    conversations = get_all_conversations(session_data)
    try:
        
        questions = get_questions(conversations,session_data)
        logger.info(f'found questions from gpt.')
        return JSONResponse(content={"data": questions}, status_code=200)
    except Exception as e:
        logger.error(
            f"failed to load sample questions with error {str(e)}",
        )
        message_content = {"message": f"failed to load sample questions with error {str(e)}"}
        return JSONResponse(
            content=message_content,
            status_code=404,
        )

@app.get("/review-count")
async def get_research_count():
    try:
        df = load_data_to_dataframe()
        review_count = count_reviews(df)
        logger.info(f'found review count, {review_count}')
        return JSONResponse(content=review_count, status_code=200)
    except Exception as e:
        logger.error(
            f"failed to load research count with error {str(e)}",
        )
        message_content = {"message": f"failed to load research count with error {str(e)}"}
        return JSONResponse(
            content=message_content,
            status_code=404,
        )

@app.get("/users/{session_guid}/conversations/{conversation_id}/chat_new/{user_question}")
async def chat_new(
    user_question,
    conversation_id,
    background_tasks: BackgroundTasks,
    session_data: UserSession = Depends(get_session_from_session),
):
    try:
        conversation = get_conversation(conversation_id, session_data)
        if conversation_id==0 or conversation_id=="0":
            conversation_id = conversation.id

        history = get_history_as_messages(conversation_id)
        graph = GraphFinder(session_data, user_question)

        topics = graph.get_topic_list_from_question()
        logger.info(f"retrieved topic {topics[0].get('name')} with score: {topics[0].get('score')}")
       
        topic = topics[0].get('name', 'unable to match topic from graph')

        logger.info("topic is " + topic)
        all_considerations = graph.get_relationships('Consideration',topic)
        
        c = Considerations(session_data, user_question)

        try:
            await c.run_all_async(history, all_considerations, conversation)
        except Exception as e:
            logger.error(
                f"failed to run_all_async with error {str(e)}",
            )
            raise e

        responder = QnAResponse(user_question, session_data, conversation)
   
        missing_considerations, matching_considerations = c.match_profile_to_graph(all_considerations)

        logger.info(f"missing_considerations: {missing_considerations}")
        kickback_response = await responder.kickback_response_async(missing_considerations, history)
        rag_response, rag_content = await responder.rag_response_async(history, matching_considerations)

        logger.info(f"recieved response on rag request: {rag_response}")

        if topics[0].get('score') < 0.74:
            kickback_response = ""
        
        conversation.topic = topic

        final_response = {
            "conversation_reference": conversation_to_dict(conversation),
            "kickback_response": kickback_response,
            "rag_response": rag_response
        }
        try:
            logger.info(f"Updating conversation history with response details")
            update_conversation_history(final_response, conversation, rag_content, session_data, user_question)
        except Exception as e:
            logger.error(
                f"failed to update_conversation_history with error {str(e)}",
            )
            raise e
        logger.info("SUCCESS!  Returning response to client")
        return JSONResponse(content=final_response, status_code=200)
    except Exception as e:
        logger.error(
            f"failed to chat_new with error {str(e)}",
        )
        return JSONResponse(
            content={"message": f"failed to return chat response with error {str(e)}"},
            status_code=404,
        )

@app.get("/users/{session_guid}/outcomes/{conversation_id}")
async def get_outcomes(
    conversation_id,
    session_data: UserSession = Depends(get_session_from_session),
):
    message_content = get_last_response(conversation_id)
    final_response = {
            "risks": '',
            "opportunities": ''
        }
    
    if not message_content or not message_content.content:
        logger.error(
            f"failed to get last response for outcome scoring.  No message content.",
        )
        return JSONResponse(content=final_response, status_code=200)
    
    logger.info(f"got last response for outcome scoring: {message_content.content}")
    finder = GraphFinder(session_data, message_content.content)
    try:
        topics = finder.get_topic_list_from_question()
        logger.info(f"retrieved topic {topics[0].get('name')} with score: {topics[0].get('score')}")

        if topics[0].get('score') < 0.73:
            return JSONResponse(content=final_response, status_code=200)
        else:
            topic = topics[0].get('name')
            risks, opportunities = finder.get_relationships('Outcome',topic)
            final_response = {
            "risks": risks,
            "opportunities": opportunities
        }

        return JSONResponse(content=final_response, status_code=200)
    except Exception as e:
        logger.error(
            f"failed to get outcomes with error {str(e)}",
        )
        message_content = {"message": f"failed to get outcomes with error {str(e)}"}
        return JSONResponse(
            content=message_content,
            status_code=200,
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
            conversation_topics = get_all_conversations(session_data)

        if not conversation_topics:
            logger.info('no conversations found for user, returning 204')
            return Response(
                status_code=204
            )
        else:
            logger.info(
                f"got conversations from documents.",
            )
            response = JSONResponse(
                content=conversation_topics, status_code=200
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

# Provide feedback on conversation
@app.post("/users/{session_guid}/conversations/{conversation_id}/messages/{message_id}")
async def response_feedback(
    session_guid, conversation_id, message_id, feedback: Feedback, session_data: UserSession = Depends(get_session_from_session)
):
    logger.info(f"CONVERSATION_ID: {conversation_id}, MESSAGE_ID: {message_id}, SESSION_ID: {session_guid}, FEEDBACK: {feedback}")
    set_context_from_session_data(session_data)
    conversation = get_conversation(conversation_id, session_data)
    logger.info(f"Got conversation: {conversation}")
    try:
        update_conversation_history_with_feedback(feedback, message_id, session_data)
        logger.info(f"Feedback success! {feedback}")
        return JSONResponse(content="Successfully recorded feedback", status_code=200)
    except Exception as e:
        logger.info(f"Feedback failed to submit! {feedback}")
        logger.error(
            f"failed to update_conversation_history with error {str(e)}",
        )
        return JSONResponse(
            content={"message": f"failed to record feedback with error {str(e)}"},
            status_code=500,
        )
