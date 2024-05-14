import pytest
import json
import mongomock

from bson import ObjectId
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from ..app import app, get_session_from_session
from ..data.models import UserSession, Profile, ConversationSimple, RawChatMessage, Feedback
from ..app_auth.authorize_user import credentials_exception
from ..conversation.update_conversation import update_conversation_history

from .mocks.mock_services import (
    MockAzureSearchService,
    MockAzureLLMClients,
)

conversation_id = "65c2e349f3c2e2aff6f2c1b3"
test_session = "480e2a18-9c95-4958-bde5-75e0d1dd1a46"


connect(
    "mongoenginetest",
    host="mongodb://localhost",
    mongo_client_class=mongomock.MongoClient,
)


@pytest.fixture(scope="session")
def mock_services(session_mocker):
    session_mocker.patch(
        "cloud_services.llm_services.AzureLLMClients", MockAzureLLMClients
    )
    session_mocker.patch(
        "cloud_services.azure_cog_service.AzureSearchService", MockAzureSearchService
    )


@pytest.fixture(scope="session")
def user_session():
    user_session = UserSession(
        user_id="test",
        session_id=test_session,
        session_start=datetime.now(),
        session_end=datetime.now() + timedelta(minutes=30),
    )
    user_session.save()
    profile = Profile(
        user_id="test",
    )
    profile.save()
    try:
        conversation = ConversationSimple(
            user_id=user_session.user_id, id=ObjectId(conversation_id)
        )
        conversation.save()
    except:
        ConversationSimple.objects(user_id="test").delete()
    yield user_session
    user_session.delete()


@pytest.fixture
def unauthenticated_client():
    def unauthorized_user(session_guid: str):
        raise credentials_exception

    app.dependency_overrides[get_session_from_session] = unauthorized_user
    return TestClient(app)


@pytest.fixture()
def authenticated_client():
    def authorized_user(session_guid: str):
        return UserSession.objects(session_id=test_session).first()

    app.dependency_overrides[get_session_from_session] = authorized_user
    yield TestClient(app)


def test_user_questions_success(mock_services, authenticated_client, user_session):
    response = authenticated_client.get(f"/users/{test_session}/questions")
    assert response.status_code == 200


def test_user_questions_unauthorized(unauthenticated_client):
    response = unauthenticated_client.get(f"/users/{test_session}/questions")
    assert response.status_code == 401


@pytest.mark.skip(reason="refactor")
def test_user_chat_success(mock_services, authenticated_client, user_session):
    response = authenticated_client.get(
        f"/users/{test_session}/conversations/{conversation_id}/chat_new/hello"
    )
    assert response.status_code == 200


@pytest.mark.skip(reason="refactor")
def test_user_chat_not_found(mock_services, authenticated_client):
    response = authenticated_client.get(
        f"/users/{test_session}/conversations/test/chat_new/hello"
    )
    assert response.status_code == 404


@pytest.mark.skip(reason="refactor")
def test_user_chat_exception_raised(mock_services, authenticated_client):
    response = authenticated_client.get(
        f"/users/{test_session}/conversations/test/chat_new/hello"
    )
    assert response.status_code == 404


@pytest.mark.skip(reason="refactor")
def test_user_chat_unauthorized(unauthenticated_client):
    response = unauthenticated_client.get(
        f"/users/{test_session}/conversations/test/chat_new/hello"
    )
    assert response.status_code == 401


def test_user_conversation_list_success(
    mock_services, authenticated_client, user_session
):
    response = authenticated_client.get(f"/users/{test_session}/conversations")
    assert response.status_code == 200


def test_user_conversation_list_unauthorized(unauthenticated_client):
    response = unauthenticated_client.get(f"/users/{test_session}/conversations")
    assert response.status_code == 401


def test_user_conversation_message_history_success(
    mock_services, authenticated_client, user_session
):
    response = authenticated_client.get(
        f"/users/{test_session}/conversations/{conversation_id}/messages"
    )
    assert response.status_code == 200


def test_user_conversation_message_history_not_found(
    mock_services, authenticated_client
):
    response = authenticated_client.get(
        f"/users/{test_session}/conversations/test/messages"
    )
    assert response.status_code == 404


def test_user_conversation_message_history_unauthorized(unauthenticated_client):
    response = unauthenticated_client.get(
        f"/users/{test_session}/conversations/test/messages"
    )
    assert response.status_code == 401

@pytest.mark.skip(reason="WIP")
def test_user_conversation_message_feedback_success(
    mock_services, authenticated_client, user_session
):
    feedback_payload = {"q1_usefullness":  {"scale": 3, "comment": "hi"}, "q2_relevancy": {"scale": 3, "comment": "bye"}, "q3_accuracy": {"scale": 5, "comment": "blah"}}
    message_id = message.message[0].id
    response = authenticated_client.post(
        f"/users/{test_session}/conversations/{conversation_id}/messages/{message_id}", json=feedback_payload
    )
    assert response.status_code == 200

    conversation = ConversationSimple(user_id=user_session.user_id, id=ObjectId(conversation_id))
    messages = conversation.history
    assert messages[-1].feedback == Feedback(**feedback_payload).dict()

def test_user_conversation_message_feedback_unauthorized(unauthenticated_client):
    feedback_payload = {"q1_usefullness":  {"scale": 3, "comment": "hi"}, "q2_relevancy": {"scale": 3, "comment": "bye"}, "q3_accuracy": {"scale": 5, "comment": "blah"}}
    message_id = 0
    response = unauthenticated_client.post(
        f"/users/{test_session}/conversations/{conversation_id}/messages/{message_id}", json=feedback_payload
    )
    assert response.status_code == 401

def test_user_conversation_message_feedback_failure(
    mock_services, authenticated_client, user_session
):
    # Invalid rating score in payload
    feedback_payload = {"q1_usefullness":  {"scale": 8, "comment": "hi"}, "q2_relevancy": {"scale": 3, "comment": "bye"}, "q3_accuracy": {"scale": 5, "comment": "blah"}}
    response = authenticated_client.post(
        f"/users/{test_session}/conversations/{conversation_id}/messages/0", json=feedback_payload
    )
    assert response.status_code == 422
