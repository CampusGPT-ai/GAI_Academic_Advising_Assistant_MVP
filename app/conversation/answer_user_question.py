
from settings.settings import Settings
from user.get_user_info import UserInfo

from conversation.retrieve_docs import SearchRetriever
from conversation.prompt_templates.kick_back_prompt import get_gpt_system_prompt as kick_back_prompt
from conversation.prompt_templates.gpt_qa_prompt import get_gpt_system_prompt as gpt_qa_prompt

import asyncio
from cloud_services.connect_mongo import MongoConnection


from conversation.run_chat import QueryLLM
import json

from data.models import ConversationSimple as Conversation, UserSession
import logging
logger = logging.getLogger(__name__)
settings = Settings()


class QnAResponse:
    def __init__(self, user_question, user_session: UserSession, conversation: Conversation):

        self.conversation = conversation
        self.user_question = user_question
        self.user_session = user_session
        self.user_id = user_session.user_id
        self.retriever = SearchRetriever.with_default_settings()
        self.user_info = UserInfo(self.user_id)
        self.llm_query = QueryLLM(user_session)
        self.user_considerations = []
        self.set_user_considerations()

    def set_user_considerations(self):
        self.user_considerations = self.user_info.get_user_info().considerations
        return

    def get_user_context(self):
        return (self.user_question + json.dumps(self.user_considerations))

    def run_rag(self):
        result = self.retriever.retrieve_content(self.get_user_context(), n=4)
        rag_links = result['source']
        rag_content = result['content']
        return rag_links, rag_content
        
        
    def rag_response(self, conversation_history):
        rag_links, rag_content = self.run_rag()
        mapped_list = [{"link": link, "response": response} for link, response in zip(rag_links, rag_content)]
        json_string = json.dumps(mapped_list, indent=4)
        rag_prompt, rag_json = self.llm_query.create_prompt_template(
            gpt_qa_prompt(self.get_user_context(),json_string),conversation_history, self.user_question)
        return self.llm_query.run_llm(rag_prompt, rag_json)
    
    async def rag_response_async(self, conversation_history):
        result = await asyncio.to_thread(self.rag_response, conversation_history)
        return result

    def kickback_response(self, missing_considerations, conversation_history):
        kickback_prompt, kickback_json = self.llm_query.create_prompt_template(
                kick_back_prompt(self.user_question, self.get_user_context(), missing_considerations), conversation_history)
        return self.llm_query.run_llm(kickback_prompt, kickback_json) 

    async def kickback_response_async(self, missing_considerations, conversation_history):
        return await asyncio.to_thread(self.kickback_response, missing_considerations, conversation_history)   

if __name__ == "__main__":

    from pathlib import Path
    from mongoengine import connect
    import os

    USER_QUESTION = "Yes I do prefer having flexible options"
    USER_ID = "A_iXG9LQjG86PTY1sgG-Sm9JO3IbMlliRkZok3BhT8I"

    db_name = os.getenv("MONGO_DB")
    db_conn = os.getenv("MONGO_CONN_STR")
    _mongo_conn = connect(db=db_name, host=db_conn)

    relative_path = Path('./app/data/mock_user_session.json')
    from conversation.retrieve_messages import get_history_as_messages
    from conversation.retrieve_conversations import conversation_to_dict
    from conversation.run_graph import GraphFinder  
    from conversation.check_considerations import Considerations
    from conversation.update_conversation import update_conversation_history

    with relative_path.open(mode='r') as file:
        mock_user_session : UserSession = UserSession(**json.load(file))
    
    # mock_conversation = Conversation(id="65cd0b42372b404efb9805f6", user_id=USER_ID)

    mock_conversation = Conversation.objects(id="6622fed0fcda8e6d6c33fb04").select_related(max_depth=5)

    finder = GraphFinder(mock_user_session, USER_QUESTION)
    c = Considerations(mock_user_session, USER_QUESTION)
    topic = finder.get_topic_from_question()
    all_considerations = finder.get_relationships('Consideration',topic)

    missing_considerations = c.match_profile_to_graph(all_considerations)

    event_loop = asyncio.get_event_loop()
    history = get_history_as_messages(mock_conversation[0].id)
    follow_up = QnAResponse(USER_QUESTION, mock_user_session, mock_conversation)

    conversation = mock_conversation[0]
    conversation_id = conversation.id
    user_question = USER_QUESTION
    session_data = mock_user_session
    if conversation_id==0 or conversation_id=="0":
        conversation_id = conversation.id

    history = get_history_as_messages(conversation_id)
    graph = GraphFinder(session_data, user_question)
    topic = graph.get_topic_from_question()
    all_considerations = graph.get_relationships('Consideration',topic)
    
    c = Considerations(session_data, user_question)

    event_loop = asyncio.get_event_loop()

    try:
        event_loop.run_until_complete(c.run_all_async(history, all_considerations, conversation))
    except Exception as e:
        logger.error(
            f"failed to run_all_async with error {str(e)}",
        )
        raise e

    responder = QnAResponse(user_question, session_data, conversation)
    missing_considerations = c.match_profile_to_graph(all_considerations)
    kickback_response = event_loop.run_until_complete(responder.kickback_response_async(missing_considerations, history))
    rag_response = event_loop.run_until_complete(responder.rag_response_async(history))

    final_response = {
        "conversation_reference": conversation_to_dict(conversation),
        "kickback_response": kickback_response,
        "rag_response": rag_response
    }
    try:
        update_conversation_history(final_response, conversation, session_data, user_question, conversation.topic)
    except Exception as e:
        logger.error(
            f"failed to update_conversation_history with error {str(e)}",
        )
        raise e