from data.models import Conversation, UserSession
import logging, sys, os, json
from util.logger_format import CustomFormatter
ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.handlers.clear()  
logger.addHandler(ch)  
from settings.settings import Settings
settings = Settings()
from mongoengine import *
from util.json_helper import CustomJSONEncoder

def get_message_history(conversation_id):
    try:
        conversation = Conversation.objects(id=conversation_id).select_related(max_depth=5)
        if not conversation:
            raise Exception("failed to find conversation")
        
        conversation_list = []
        message_list = []
        message_small_list = []
        citation_list = []
        for c in conversation:
            messages = c.messages
            c_dict = c._data

            for m in messages:
                raw_messages = m.message
                m_dict = m._data
                citations = m.citations

                for cit in citations:
                    cit_dict = cit._data
                    citation_list.append(cit_dict)
                
                r_dict = raw_messages._data
                r_dict["user_session_id"] = str(r_dict["user_session_id"].id)

                for r in raw_messages.message:
                    message_small_list.append(r._data)
                
                r_dict["message"]= message_small_list
                m_dict["citations"] = citation_list
                m_dict["message"] = r_dict
                message_list.append(m_dict)

            c_dict['messages'] = message_list
            conversation_list.append(c_dict)

        json_data = json.dumps(conversation_list, cls=CustomJSONEncoder)

        return json_data


    except Exception as e:
        raise Exception(f"failed to find conversation with error {str(e)}")

if __name__=="__main__":
    from mongoengine import connect
    from bson import ObjectId

    db_name = settings.MONGO_DB
    db_conn = settings.MONGO_CONN_STR
    _mongo_conn = connect(db=db_name, host=db_conn)

    conversation = Conversation.objects()
    
    from pathlib import Path
    print("Current Working Directory:", os.getcwd())
    relative_path = Path('./app/data/mock_user_session.json')


    with relative_path.open(mode='r') as file:
        mock_user_session : UserSession = UserSession(**json.load(file))
    
    get_message_history(conversation_id="65bc1f2c447ee7b27f0f8938")
