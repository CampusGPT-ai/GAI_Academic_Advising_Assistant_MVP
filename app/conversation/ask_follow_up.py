from cloud_services.llm_services import AzureLLMClients, get_llm_client
from settings.settings import Settings
from user.get_user_info import UserInfo
from cloud_services.kg_neo4j import Neo4jSession
from conversation.retrieve_docs import SearchRetriever
from conversation.prompt_templates.kick_back_prompt import get_gpt_system_prompt as kick_back_prompt
from conversation.prompt_templates.gpt_qa_prompt import get_gpt_system_prompt as gpt_qa_prompt
from conversation.prompt_templates.classify_graph_prompt import get_gpt_classification_prompt
from conversation.prompt_templates.internet_search_query import get_gpt_search_prompt
from cloud_services.openai_response_objects import Message
from cloud_services.connect_mongo import MongoConnection
from conversation.update_conversation import update_conversation_history
from threading import Thread
from cloud_services.internet_search import query_google
from conversation.run_chat import QueryLLM
import json
from queue import Queue, Empty
from data.models import ConversationSimple as Conversation, MessageContent, RawChatMessage, UserSession
import logging
logger = logging.getLogger(__name__)
settings = Settings()

USER_QUESTION = "Yes I do prefer having flexible options"
USER_ID = "A_iXG9LQjG86PTY1sgG-Sm9JO3IbMlliRkZok3BhT8I"
#will just proxy this for testing (this will be a route)
class FollowUp:
    def __init__(self, user_question, user_session: UserSession, conversation: Conversation):
        self.mongo_client = MongoConnection().connect()
        self.conversation = conversation
        
        self.user_question = user_question
        self.user_session = user_session
        self.user_id = user_session.user_id
        logger.info(f"GOT User ID: {self.user_id}")
        logger
        self.finder = None
        self.retriever = SearchRetriever.with_default_settings()
        self.user_info = UserInfo(self.user_id)
        self.llm_query = QueryLLM(user_session, conversation, self.user_info.get_user_info())
        self.risks = []
        self.opportunities = []
        self.all_considerations = []
        self.user_considerations = None
        self.graph_considerations = []
        self.related_topics = None
        self.rag = []
        self.rag_links = []
        self.missing_considerations = []
        self.user = self.user_info.user_profile
        self.thread_pool = {}
        self.response_pool = Queue()
        self.error_q = Queue()
        self.rag_response = None
        self.topic = ''
        self.set_user_considerations()

    def set_user_considerations(self):
        self.user_considerations = self.user_info.get_user_info().considerations
        return

    def get_user_context(self):
        return (self.user_question + json.dumps(self.user_considerations))

    def find_nodes(self):
        if self.finder == None:
            self.init_neo4j()
        self.related_topics = self.finder.find_similar_nodes(self.user_question)

    def find_all_nodes(self):
        if self.finder == None:
            self.init_neo4j()
        self.all_considerations = self.finder.find_all_nodes()

    def find_relationships(self, type):
        if self.finder == None:
            self.init_neo4j()
        if type == 'Consideration':
            self.graph_considerations = self.finder.query_considerations(self.related_topics, type, 'IS_CONSIDERATION_FOR')
        elif type == 'Outcome':
            self.risks = self.finder.query_outcomes('IS_RISK_OF',self.related_topics)
            self.opportunities = self.finder.query_outcomes('IS_OPPORTUNITY_FOR', self.related_topics)

    def init_neo4j(self):
        if self.finder == None:
            self.finder = Neo4jSession(settings.N4J_URI, settings.N4J_USERNAME, settings.N4J_PASSWORD)

    def get_initial_graph(self):
        if self.finder == None:
            self.init_neo4j()

        topic_thread = Thread(target=self.find_nodes)
        topic_thread.start()
        self.thread_pool['topic_thread'] = topic_thread

        consideration_thread = Thread(target=self.find_all_nodes)
        consideration_thread.start()
        self.thread_pool['all_consideration_thread'] = consideration_thread
        
    def run_graph_info(self):
        if self.finder == None:
            self.init_neo4j()

        graph_consideration_thread = Thread(target=self.find_relationships, args=('Consideration',))
        outcome_thread = Thread(target=self.find_relationships, args=('Outcome',))
        graph_consideration_thread.start()
        outcome_thread.start()

        self.thread_pool['graph_consideration_thread'] = graph_consideration_thread
        self.thread_pool['outcome_thread'] = outcome_thread
    
    def get_consideration_keys(self):
        keys = []
        for consideration in self.user_considerations:
            key = consideration.keys()
            keys.extend(list(key))
        return keys
    
    def get_consideration_descriptions(self, name):
        descriptions = []
        for consideration in self.user_considerations:
            if consideration.keys() == name:
                descriptions.append(consideration.values())
        return descriptions

    def match_profile_to_graph(self):
        profile_considerations = self.get_consideration_keys()
        self.missing_considerations = []

        if self.thread_pool['graph_consideration_thread'].is_alive():
            self.thread_pool['graph_consideration_thread'].join()

        for consideration in self.graph_considerations:
            if consideration.get('name') not in profile_considerations:
                self.missing_considerations.append(consideration)
        return
    
    def get_conversation_history(self):
        try:
            data = self.conversation._data
            history = data.get('history')
            history = history[1:] if history[0].get('role') == 'system' else history
            if history is None:
                history = []
            if len(history) < 5:
                return history
            else:
                return history[-5:]
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

    def match_llm_to_profile(self, new_considerations):

        self.missing_considerations = self.user_considerations
        consideration_dictionary = {}
        for consideration in new_considerations.get('considerations'):
            self.missing_considerations.append({consideration.get('name'): consideration.get('user information')})

        list_tuples = {tuple(d.items())[0] for d in self.missing_considerations}

        for (n,d) in list_tuples:
            if n not in consideration_dictionary:
                consideration_dictionary[n] = d
            else:
                consideration_dictionary[n] = d + ", " + consideration_dictionary[n]

        self.missing_considerations = [{k: v} for k, v in consideration_dictionary.items()]

        return

    def run_rag(self, user_context):
        result = self.retriever.retrieve_content(user_context, n=4)
        self.rag_links = result['source']
        self.rag_response = result['content']
        return
        
    def return_conversation_reference(self):
        if self.conversation: 
            c_dict = {
                "topic": self.topic,
                "id": str(self.conversation.id),
                "start_time": self.conversation.start_time.isoformat() if self.conversation.start_time else None,
                "end_time":self.conversation.end_time.isoformat() if self.conversation.end_time else None,
            }

        return c_dict

    def update_considerations(self, new_considerations):
        if self.mongo_client == None:
            self.init_mongo()
        
        self.match_llm_to_profile(new_considerations)

        try:
            self.user.considerations = self.missing_considerations
            self.user.active_conversation = self.conversation
            self.user.save()
            return True
        except Exception as e:
            logger.error(f"Error saving considerations: {e}")
            return e
            
    def run_llm(self, prompt, expected_json = [], name = None):
        try:
            formatted_response = self.llm_query.run_llm(prompt, self.error_q, expected_json)
            if self.error_q.empty():
                logger.info(f"formatted response: {formatted_response}")
                self.response_pool.put({name:formatted_response}) 
        except Exception as e:
            raise e



    def full_response(self, topic):
        from conversation.retrieve_messages import get_history_as_messages
        try:
            conversation_history = get_history_as_messages(self.conversation.id)
            
            user_context = self.get_user_context()
            yield {"event": "notification", "data": json.dumps({'message': 'got user context from backend'})}

            rag = Thread(target=self.run_rag, args=(user_context,))
            rag.start()
            self.thread_pool['rag_thread'] = rag

            self.get_initial_graph()
            self.thread_pool['topic_thread'].join()

            self.run_graph_info()
    

            if not self.error_q.empty():
                yield {"event": "error_message", "data": json.dumps({'message': 'Error getting considerations response'})}
                raise (self.error_q.get())
            
            if considerations_response:
                considerations_response = considerations_response.get('new_considerations')


            yield {"event": "notification", "data": json.dumps({'message': f'received considerations response {considerations_response}'})}

            if considerations_response.get('contains considerations') == 'yes':
                try_update = self.update_considerations(considerations_response)
                yield {"event": "notification", "data": json.dumps({'message': 'got user context from backend'})}

                if not try_update:
                    logger.error("Error updating user considerations")
                
            user_context = self.get_user_context()

            self.thread_pool['rag_thread'].join()

            mapped_list = [{"link": link, "response": response} for link, response in zip(self.rag_links, self.rag_response)]
            json_string = json.dumps(mapped_list, indent=4)

            self.thread_pool['graph_consideration_thread'].join()
            self.match_profile_to_graph()

            rag_prompt, rag_json = self.llm_query.create_prompt_template(
                gpt_qa_prompt(user_context,json_string),conversation_history, self.user_question)
            kickback_prompt, kickback_json = self.llm_query.create_prompt_template(
                kick_back_prompt(self.user_question, user_context, self.missing_considerations), conversation_history)
            

            
            # process rag and follow up question in parallel
            rag_thread = Thread(target=self.run_llm, args=(rag_prompt, rag_json,"rag_response"))
            kickback_thread = Thread(target=self.run_llm, args=(kickback_prompt,kickback_json,"kickback_response"))
            rag_thread.start()
            kickback_thread.start()
            
            rag_thread.join()
            yield {"event": "notification", "data": json.dumps({'message': f'got to rag response.' })}


            kickback_thread.join()
            yield {"event": "notification", "data": json.dumps({'message': f'got to kickback response.' })}
            responses = []
            isError = False

            if self.risks:
                yield {"event": "risks", "data": json.dumps({'message': self.risks})}
            if self.opportunities:
                yield {"event": "opportunities", "data": json.dumps({'message': self.opportunities})}
            
            while not self.response_pool.empty() and not isError and self.error_q.empty():
                item = self.response_pool.get_nowait()
                item_key = None
                if type(item) == dict:
                    item_key = next(iter(item))  # Or q.get(block=False)
                if item_key == 'rag_response':
                    try:
                        item = item[item_key]
                        self.topic = item['topic']
                        responses.append(item)
                        yield {"event": item_key, "data": json.dumps({'message' : item})}
                    except Exception as e:
                        logger.error(f"Error processing rag response: {str(e)}")
                        yield {"event": "error_message", "data": json.dumps({'message': f'Error processing rag response {str(e)}'})}
                        isError = True
                if item_key == 'kickback_response':
                    item = item[item_key]
                    responses.append(item)
                    yield {"event": item_key, "data": json.dumps({'message' : item})}
                    #mprint(f'got to kickback response.  Len responses {len(responses)}.  Queue size {self.response_pool.qsize()}. IsError {isError}')
            print('got to break')
            if responses and len(responses) > 0:
                logger.info('updating conversation history with responses')
                update_conversation_history(responses, self.conversation, self.user_session, self.user_question, self.topic)
        except Empty: 
            logger.info('Queue is empty')
        except Exception as e:
            logger.error(f"Error processing responses: {str(e)}")
            yield {"event": "error_message", "data": json.dumps({'message': f'Error processing responses {str(e)}'})}
            isError = True
        except GeneratorExit:
            logger.info("Generator clean-up on closure")
            raise
        finally:
            print('finally block')
            yield {"event": "stream-ended", "data": json.dumps({'stream-ended': 'true'})}
            try:
                if self.finder:
                    self.finder.close()
            except Exception as e:
                logger.info(f"Error closing neo4j session: {e}")
    
if __name__ == "__main__":

    from pathlib import Path
    from mongoengine import connect
    import os

    db_name = os.getenv("MONGO_DB")
    db_conn = os.getenv("MONGO_CONN_STR")
    _mongo_conn = connect(db=db_name, host=db_conn)



    relative_path = Path('./app/data/mock_user_session.json')


    with relative_path.open(mode='r') as file:
        mock_user_session : UserSession = UserSession(**json.load(file))
    
    # mock_conversation = Conversation(id="65cd0b42372b404efb9805f6", user_id=USER_ID)

    mock_conversation = Conversation.objects(id="661aa0de5d7fa5744cf4392e").select_related(max_depth=5)

    follow_up = FollowUp(USER_QUESTION, mock_user_session, mock_conversation[0])
    try:
        result = follow_up.full_response()
        while True: 
            r = next(result)
            print(r)
    except Exception as e:
        print(f"Error: {str(e)}")
        
        
