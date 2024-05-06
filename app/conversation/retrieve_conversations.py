import logging
from data.models import ConversationSimple
logger = logging.getLogger(__name__)

def get_conversation(conversation_id, session_data):
    try:
        if conversation_id == "0" or conversation_id == 0:
                logger.info(
                    "saving new conversation",
                )
                conversation = ConversationSimple(user_id=session_data.user_id, topic="No topic")

                conversation.save()
                logger.info(
                    f"got conversation information {conversation.id}",
                )
        else:
            conversation = ConversationSimple.objects(id=conversation_id).select_related(max_depth=5)
            conversation = conversation[0]

        if conversation is None:
            raise Exception("unable to create conversation for user chat.")
        return conversation
    except Exception as e:
        raise e

def remove_partial_conversation(conversation_id):
    try:
        conversation = ConversationSimple.objects(id=conversation_id)
        conversation = conversation[0]
        if conversation.history == []:
            logger.info('removing partial conversation for user')
            conversation.delete()
        return True
    except Exception as e:
        raise e
    
def conversation_to_dict(c):
    return {
                    "topic": c.topic if c.topic else "No topic",
                    "id": str(c.id),
                    "start_time": c.start_time.isoformat() if c.start_time else None,
                    "end_time": c.end_time.isoformat() if c.end_time else None,
                }

def remove_empty_conversations():
    try:
        conversations = ConversationSimple.objects()
        for conversation in conversations:
            if conversation.history == []:
                conversation.delete()
        return True
    except Exception as e:
        raise e
    
def get_all_conversations(session_data):
    try:
        conversations = ConversationSimple.objects(
                user_id=session_data.user_id
            )
        if not conversations:
            return False
        conversation_topics = []
        if conversations:
            for c in conversations:
                c_dict = conversation_to_dict(c)
                conversation_topics.append(c_dict) 
        else:
            raise
        return conversation_topics
    except Exception as e:
        raise e
    
if __name__=="__main__":
    from pathlib import Path
    import json
    from data.models import UserSession
    from cloud_services.connect_mongo import MongoConnection
    from data.models import ConversationSimple as Conversation

    mongo_conn = MongoConnection()
    mongo_conn.connect()

    relative_path = Path('./app/data/mock_user_session.json')
    with relative_path.open(mode='r') as file:
        mock_user_session : UserSession = UserSession(**json.load(file))

    mock_conversation = Conversation.objects(id="661c808ff27652f2a0840d5d").select_related(max_depth=5)

    conversation = get_conversation("0", mock_user_session)
    remove_partial_conversation(conversation.id)
    conversation_dict = conversation_to_dict(conversation)
    remove_empty_conversations()
    print(conversation_dict)

