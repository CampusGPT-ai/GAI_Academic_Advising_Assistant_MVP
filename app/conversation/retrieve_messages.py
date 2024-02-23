from data.models import Conversation, UserSession
import logging, sys, os, json

logger = logging.getLogger(__name__)

from settings.settings import Settings
settings = Settings()
from mongoengine import *
from util.json_helper import CustomJSONEncoder

def get_message_history(conversation_id, return_type = "json"):
    try:
        conversation = Conversation.objects(id=conversation_id).select_related(max_depth=5)
        if not conversation:
            raise Exception(f"failed to find conversation for {conversation_id}")
        
        message_list = []

        # should always be one but query returns array
        for c in conversation:
            messages = c.messages

            #data contains topic, start, end, id
            #messages are a list of message objects that need to be parsed further
            c_dict = c._data
            c_dict["id"]=str(c_dict["id"])
            del c_dict['messages']

            for m in messages:

                #data contains two chat messages with references (follow ups, citations)
                m_dict = m._data

                citation_list = []
                for cit in m.citations:
                    cit_dict = cit._data
                    citation_list.append(cit_dict)
                
                m_dict['citations'] = citation_list
                
                new_message = {}

                #get chats
                message_small_list = []
                for r in m.message.message:
                    message_small_list.append(r._data)

                message_small_list = sorted(message_small_list, key=lambda x: (x['role']), reverse=True)

                for role in message_small_list:
                    new_message = role
                    if role["role"] == 'assistant':
                        new_message["citations"]=citation_list
                        new_message["followups"]=m_dict["follow_up_questions"]
                    message_list.append(new_message)
        sorted_messages = sorted(message_list, key=lambda x: (x['created_at']), reverse=False)

        json_data = json.dumps(sorted_messages, cls=CustomJSONEncoder)

        if return_type == 'json':
            return json_data
        else:
            return sorted_messages


    except Exception as e:
        raise Exception(f"failed to find conversation with error {str(e)}")

if __name__=="__main__":
    from mongoengine import connect

    db_name = settings.MONGO_DB
    db_conn = settings.MONGO_CONN_STR
    _mongo_conn = connect(db=db_name, host=db_conn)

    conversation = Conversation.objects()
    
    from pathlib import Path
    logger.debug("Current Working Directory:", os.getcwd())
    relative_path = Path('./app/data/mock_user_session.json')


    with relative_path.open(mode='r') as file:
        mock_user_session : UserSession = UserSession(**json.load(file))
    
    get_message_history(conversation_id="65bc1e6b24ea835e402e6b1b")

