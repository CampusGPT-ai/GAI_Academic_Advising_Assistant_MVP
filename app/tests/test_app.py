import asyncio
import pytest
import mongomock

from bson import ObjectId
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from httpx import AsyncClient
from mongoengine import connect, disconnect

from ..app import app, get_session_from_session
from ..data.models import UserSession, Conversation
from ..app_auth.authorize_user import credentials_exception


conversation_id = "65c2e349f3c2e2aff6f2c1b3"
test_session = "480e2a18-9c95-4958-bde5-75e0d1dd1a46"


def handle_streaming_response():
    def before_record_response(response):
        if response.get("is_streaming"):
            response.read()
        if response.get("is_error"):
            response.read()
        return response

    return before_record_response


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "ignore_hosts": ["localhost", "testserver"],
        "filter_headers": ["authorization", "api-key"],
    }


@pytest.fixture()
def unauthenticated_client():
    def unauthorized_user(session_guid: str):
        raise credentials_exception

    app.dependency_overrides[get_session_from_session] = unauthorized_user
    return TestClient(app)


@pytest.fixture()
def authenticated_client():
    connect(
        "mongoenginetest",
        host="mongodb://localhost",
        mongo_client_class=mongomock.MongoClient,
    )

    def authorized_user(session_guid: str):
        user_session = UserSession(
            user_id="test",
            session_id=test_session,
            session_start=datetime.now(),
            session_end=datetime.now() + timedelta(minutes=30),
        )
        user_session.save()
        try:
            conversation = Conversation(
                user_id=user_session.user_id, id=ObjectId(conversation_id)
            )
            conversation.save()
        except:
            Conversation.objects(user_id="test").delete()
        yield user_session

    app.dependency_overrides[get_session_from_session] = authorized_user
    yield TestClient(app)
    disconnect()


@pytest.mark.vcr
def test_user_questions_success(authenticated_client):
    response = authenticated_client.get(f"/users/{test_session}/questions")
    assert response.status_code == 200


@pytest.mark.vcr
def test_user_questions_unauthorized(unauthenticated_client):
    response = unauthenticated_client.get(f"/users/{test_session}/questions")
    assert response.status_code == 401


@pytest.mark.vcr(before_record_response=handle_streaming_response())
def test_user_chat_success(authenticated_client):
    response = authenticated_client.get(
        f"/users/{test_session}/conversations/{conversation_id}/chat/hello"
    )
    assert response.status_code == 200


@pytest.mark.vcr
def test_user_chat_not_found(authenticated_client):
    response = authenticated_client.get(f"/users/{test_session}/conversations/test/chat/hello")
    assert response.status_code == 404


@pytest.mark.vcr
def test_user_chat_exception_raised(authenticated_client):
    response = authenticated_client.get(f"/users/{test_session}/conversations/test/chat/hello")
    assert response.status_code == 404


@pytest.mark.vcr
def test_user_chat_unauthorized(unauthenticated_client):
    response = unauthenticated_client.get(f"/users/{test_session}/conversations/test/chat/hello")
    assert response.status_code == 401


@pytest.mark.skip
@pytest.mark.vcr(before_record_response=handle_streaming_response())
@pytest.mark.anyio
async def test_user_conversations_success(authenticated_client):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            f"/users/{test_session}/conversations/{conversation_id}/chat/hello"
        )
        assert response.status_code == 200
        response = await ac.get(f"/users/{test_session}/conversations")
        assert response.status_code == 200


@pytest.mark.vcr
def test_user_conversation_list_unauthorized(unauthenticated_client):
    response = unauthenticated_client.get(f"/users/{test_session}/conversations")
    assert response.status_code == 401


@pytest.mark.skip
@pytest.mark.vcr(before_record_response=handle_streaming_response())
@pytest.mark.anyio
async def test_user_conversation_message_history_success(authenticated_client):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            f"/users/{test_session}/conversations/{conversation_id}/chat/hello"
        )
        assert response.status_code == 200
        response = await ac.get(f"/users/{test_session}/conversations/{conversation_id}/messages")
        assert response.status_code == 200


@pytest.mark.vcr
def test_user_conversation_message_history_not_found(authenticated_client):
    response = authenticated_client.get(f"/users/{test_session}/conversations/test/messages")
    assert response.status_code == 404


@pytest.mark.vcr
def test_user_conversation_message_history_unauthorized(unauthenticated_client):
    response = unauthenticated_client.get(f"/users/{test_session}/conversations/test/messages")
    assert response.status_code == 401
