
from settings.settings import Settings
from user.get_user_info import UserInfo

from conversation.retrieve_docs import SearchRetriever
from conversation.prompt_templates.kick_back_prompt import get_gpt_system_prompt as kick_back_prompt
from conversation.prompt_templates.gpt_qa_prompt import get_gpt_system_prompt as gpt_qa_prompt

import asyncio
from cloud_services.connect_mongo import MongoConnection
from graph_update.graph_eval_and_update import NodeEditor

from conversation.run_chat import QueryLLM
import json

from evaluation_metrics.qa_retrieval_eval import RetrievalEval
from data.models import ConversationSimple as Conversation, UserSession
import logging
logger = logging.getLogger(__name__)
settings = Settings()


class QnAResponse:
    def __init__(self, user_question, user_session: UserSession, conversation: Conversation):

        self.conversation = conversation
        self.user_question = user_question
        self.rag_results = None
        self.user_session = user_session
        self.user_id = user_session.user_id
        self.retriever = SearchRetriever.with_default_settings()
        self.user_info = UserInfo(self.user_id)
        self.llm_query = QueryLLM(user_session)
        self.user_considerations = []
        self.set_user_considerations()

    def set_user_considerations(self):
        info = self.user_info.get_user_info()
        if info.considerations:
            self.user_considerations = self.user_info.get_user_info().considerations
        else:
            'No considerations found in user profile.'
        return

    def get_user_context(self):
        return (self.user_question + json.dumps(self.user_considerations))

    def run_rag(self):
        rag_links, rag_content = [], []
        retriever = RetrievalEval()
        retriever.get_results(self.user_question, 30, 'hybrid')
        logger.info("got retrieval results")
        retriever.calculate_columns()
        logger.info("calculated columns")
        if len(retriever.results) > 0:
            retriever.group_results(5)
            logger.info("grouped results")
            rag_dict = retriever.results.to_dict(orient='records')

        for item in rag_dict:
            rag_links.append(item.get("source"))
            rag_content.append(item.get('content'))
        logger.info("returning rag result")
        return rag_links, rag_content
        
        
    def rag_response(self, conversation_history, matching_considerations):
        try:
            rag_links, rag_content = self.run_rag()
            try:
                mapped_list = [{"response": response, "link": link} for link, response in zip(rag_links, rag_content)]
                json_string = json.dumps(mapped_list, indent=4)
                self.rag_results = json_string
            except Exception as e:
                logger.error(f"unable to map Rag response to list with error: {str(e)}")
                raise e
            rag_prompt, rag_json = self.llm_query.create_prompt_template(
                gpt_qa_prompt(" ".join(matching_considerations),json_string),conversation_history, self.user_question)
            return self.llm_query.run_llm(rag_prompt, rag_json)
        except Exception as e:
            logger.error(f"Error returning RAG response: {str(e)}")
            raise e
    
    async def rag_response_async(self, conversation_history, matching_considerations):
        try:
            logger.info(f"running rag response for user question with {matching_considerations}")
            result = await asyncio.to_thread(self.rag_response, conversation_history, matching_considerations)
            logger.info(f"returning rag results to caller")
            return result, self.rag_results
        except Exception as e:
            raise e

    def kickback_response(self, missing_considerations, conversation_history):
        kickback_prompt, kickback_json = self.llm_query.create_prompt_template(
                kick_back_prompt(self.user_question, self.get_user_context(), missing_considerations), conversation_history)
        return self.llm_query.run_llm(kickback_prompt, kickback_json) 

    async def kickback_response_async(self, missing_considerations, conversation_history):
        logger.info(f"running kickback reponse for missing considerations")
        return await asyncio.to_thread(self.kickback_response, missing_considerations, conversation_history)   

if __name__ == "__main__":

    from pathlib import Path
    from mongoengine import connect
    import os

    USER_QUESTION = "What are the dining options on campus?"
    USER_ID = "MENelson@indianatech.edu"

    db_name = os.getenv("MONGO_DB")
    db_conn = os.getenv("MONGO_CONN_STR")
    _mongo_conn = connect(db=db_name, host=db_conn)

    # Now use the relative path
    relative_path = Path('./app/data/mock_user_session.json')

    from conversation.retrieve_messages import get_history_as_messages
    from conversation.retrieve_conversations import conversation_to_dict
    from conversation.run_graph import GraphFinder  
    from conversation.check_considerations import Considerations
    from conversation.update_conversation import update_conversation_history

    with relative_path.open(mode='r') as file:
        mock_user_session : UserSession = UserSession(**json.load(file))
    
    # mock_conversation = Conversation(id="65cd0b42372b404efb9805f6", user_id=USER_ID)

    mock_conversation = Conversation.objects(id="665b86e154456c7968a247c9").select_related(max_depth=5)

    graph = GraphFinder(mock_user_session, USER_QUESTION)

    topics = graph.get_topic_list_from_question()
    if topics[0].get('score') < 0.9:
        print('adding new topics and relationships for low scoring match')
        finder = NodeEditor(mock_user_session, USER_QUESTION)
        finder.init_neo4j()
        finder.orchestrate_graph_update_async(topics)
    
    topic = topics[0].get('name')

    c = Considerations(mock_user_session, USER_QUESTION)

    all_considerations = graph.get_relationships('Consideration',topic)

    missing_considerations, matching_considerations = c.match_profile_to_graph(all_considerations)

    history = get_history_as_messages(mock_conversation[0].id)
    follow_up = QnAResponse(USER_QUESTION, mock_user_session, mock_conversation)

    conversation = mock_conversation[0]
    conversation_id = conversation.id
    user_question = USER_QUESTION
    session_data = mock_user_session
    if conversation_id==0 or conversation_id=="0":
        conversation_id = conversation.id

    history = get_history_as_messages(conversation_id)
    all_considerations = graph.get_relationships('Consideration',topic)
    
    c = Considerations(session_data, user_question)

    try:
        asyncio.run(c.run_all_async(history, all_considerations, conversation))
    except Exception as e:
        logger.error(
            f"failed to run_all_async with error {str(e)}",
        )
        raise e
    responder = QnAResponse(user_question, session_data, conversation)
    if 'course' in topic.lower():
        responder.retriever = SearchRetriever.with_default_settings(index_name=settings.SEARCH_CATALOG_NAME)
    missing_considerations, matching_considerations = c.match_profile_to_graph(all_considerations)
    kickback_response = asyncio.run(responder.kickback_response_async(missing_considerations, history))
    rag_response, _ = asyncio.run(responder.rag_response_async(history, matching_considerations))

    if topics[0].get('score') < 0.9:
        kickback_response = ""

    final_response = {
        "conversation_reference": conversation_to_dict(conversation),
        "kickback_response": kickback_response,
        "rag_response": rag_response
    }
    
    try:
        update_conversation_history(final_response, conversation, responder.rag_results, session_data, user_question)
    except Exception as e:
        logger.error(
            f"failed to update_conversation_history with error {str(e)}",
        )
        raise e