from data.models import ConversationSimple, UserSession
import logging, sys, os, json
from cloud_services.openai_response_objects import Message
logger = logging.getLogger(__name__)

from settings.settings import Settings
settings = Settings()
from mongoengine import *
from util.json_helper import CustomJSONEncoder

def get_message_history(conversation_id, return_type = "json"):
    try:
        conversation = ConversationSimple.objects(id=conversation_id).select_related(max_depth=5)
        if not conversation:
            raise Exception(f"failed to find conversation for {conversation_id}")
        
        message_list = []

        # should always be one but query returns array
        for c in conversation:
            messages = c.history

            #data contains topic, start, end, id
            #messages are a list of message objects that need to be parsed further
            c_dict = c._data
            c_dict["id"]=str(c_dict["id"])
            del c_dict['history']

            for m in messages:

                #data contains two chat messages with references (follow ups, citations)
                m_dict = m._data

                new_message = {}

                #get chats
                message_small_list = []
                for r in m.message:
                    r_dict = r._data
                    r_dict["id"]=str(r_dict["_id"])
                    message_small_list.append(r_dict)

                message_small_list = sorted(message_small_list, key=lambda x: (x['role']), reverse=True)

                for role in message_small_list:
                    new_message = role
                    message_list.append(new_message)
        sorted_messages = sorted(message_list, key=lambda x: (x['created_at']), reverse=False)

        json_data = json.dumps(sorted_messages, cls=CustomJSONEncoder)

        if return_type == 'json':
            return json_data
        else:
            return sorted_messages


    except Exception as e:
        raise Exception(f"failed to find conversation with error {str(e)}")

def get_history_as_messages(conversation_id):

    history = get_message_history(conversation_id,'none')
    messages = []

    if isinstance(history, list) and history != []:
        for message in history:
            if isinstance(message, dict):
                message_data = message
                messages.append(Message(role=message_data['role'], content=message_data['message']))
    return messages

def get_last_response(conversation_id) -> Message:
    messages = get_history_as_messages(conversation_id)
    non_user_messages = [message for message in messages if message.role != 'user']
    if non_user_messages:
        return non_user_messages[-1]  # Get the most recent non-user message
    return None


if __name__=="__main__":
    from mongoengine import connect

    db_name = settings.MONGO_DB
    db_conn = settings.MONGO_CONN_STR
    _mongo_conn = connect(db=db_name, host=db_conn)

    conversation = ConversationSimple.objects()
    
    from pathlib import Path
    logger.debug("Current Working Directory:", os.getcwd())
    relative_path = Path('./app/data/mock_user_session.json')


    with relative_path.open(mode='r') as file:
        mock_user_session : UserSession = UserSession(**json.load(file))
    
    get_message_history(conversation_id="66438b1a16436047f729b58c")

