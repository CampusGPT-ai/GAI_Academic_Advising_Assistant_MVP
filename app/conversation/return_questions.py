from cloud_services.llm_services import get_llm_client
from conversation import run_chat
from conversation.prompt_templates import refine_questions_prompt
import json
from user.get_user_info import UserInfo

def get_questions(conversation_topics, user_session):
   
    user_info = UserInfo(user_session.user_id).get_user_info()
    user_info = user_info.to_json()
    chatter = run_chat.QueryLLM( user_session)
    topics = json.dumps(conversation_topics)
    prompt = refine_questions_prompt.get_questions_prompt(user_info,topics)
    messages, validation_keys = chatter.create_prompt_template(prompt,[],None)
    return chatter.run_llm(messages, validation_keys)

if __name__ == "__main__":

    from pathlib import Path
    from mongoengine import connect
    import os
    from data.models import UserSession, ConversationSimple

    db_name = os.getenv("MONGO_DB")
    db_conn = os.getenv("MONGO_CONN_STR")
    _mongo_conn = connect(db=db_name, host=db_conn)

    relative_path = Path('./app/data/mock_user_session.json')


    with relative_path.open(mode='r') as file:
        mock_user_session : UserSession = UserSession(**json.load(file))

    conversation_topics = ["college admissions", "financial aid", "course selection"]
    mock_conversation = ConversationSimple.objects(id="661066e1e6a80ce1f8c03546").select_related(max_depth=5)

    print(get_questions(conversation_topics, mock_user_session))