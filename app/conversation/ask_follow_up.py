from cloud_services.llm_services import AzureLLMClients, get_llm_client
from settings.settings import Settings
from user.get_user_info import UserInfo
from cloud_services.kg_neo4j import Neo4jSession
from conversation.retrieve_docs import SearchRetriever
from conversation.prompt_templates.kick_back_prompt import get_gpt_system_prompt as kick_back_prompt
from conversation.prompt_templates.gpt_qa_prompt import get_gpt_system_prompt as gpt_qa_prompt
from conversation.prompt_templates.classify_graph_prompt import get_gpt_classification_prompt
from cloud_services.openai_response_objects import Message
from cloud_services.connect_mongo import MongoConnection
from threading import Thread
import json
from queue import Queue, Empty
from data.models import ConversationSimple as Conversation, MessageContent, RawChatMessage, UserSession

settings = Settings()

USER_QUESTION = "How do I decide which electives to take for my physics degree?"
USER_ID = "A_iXG9LQjG86PTY1sgG-Sm9JO3IbMlliRkZok3BhT8I"
#will just proxy this for testing (this will be a route)

class FollowUp:
    def __init__(self, user_question, user_session: UserSession, conversation: Conversation):
        self.mongo_client = MongoConnection().connect()
        self.conversation = conversation
        self.user_question = user_question
        self.user_session = user_session
        self.user_id = user_session.user_id
        self.finder = None
        self.azure_llm_client = get_llm_client(api_type='azure',
                                                api_version=settings.OPENAI_API_VERSION,
                                                endpoint=settings.AZURE_OPENAI_ENDPOINT,
                                                model=settings.GPT4_MODEL_NAME,
                                                deployment=settings.GPT4_DEPLOYMENT_NAME,
                                                embedding_deployment=settings.EMBEDDING)
        
        self.retriever = SearchRetriever.with_default_settings()
        self.user_info = UserInfo(self.user_id)
        self.risks = []
        self.opportunities = []
        self.all_considerations = []
        self.user_considerations = None
        self.graph_considerations = []
        self.related_topics = None
        self.rag = []
        self.missing_considerations = []
        self.retry_count = 0
        self.user = self.user_info.user_profile
        self.thread_pool = {}
        self.response_pool = Queue()
        self.rag_response = None

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
            self.response_pool.put({'risks': self.risks}) if self.risks else None
            self.opportunities = self.finder.query_outcomes('IS_OPPORTUNITY_FOR', self.related_topics)
            self.response_pool.put({'opportunities': self.opportunities}) if self.opportunities else None

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

    def match_llm_to_profile(self, new_considerations):

        self.missing_considerations = self.user_considerations
        consideration_dictionary = {}

        for consideration in new_considerations:
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
        result = self.retriever.retrieve_content(user_context, n=10)
        self.rag_response = result['content']
        return
    
    # check for the existence of a key in a dictionary, to validate that the LLM response returned the expected JSON
    # should probably move this to the LLM service as it is common to all LLM JSON responses
    def validate_json(self, dict, string_list):
        output = None
        for l in string_list:
            try: 
                output = dict.get(l)
                if output:
                    return True
            except:
                continue
        return output

    
    @staticmethod
    def _format_json(gpt_response):
        response = gpt_response.choices[0].message.content
        formatted_response = response.replace("\n", "").replace(r"```", "").replace("json", "")   
        return json.loads(formatted_response)
    
    def get_conversation_history(self):
        data = self.conversation._data
        history = data.get('history')
        if len(history) < 5:
            return history
        else:
            return history[-5:]
    
    def create_prompt_template(self, input, history=False):
        messages = []

        if type(input) == tuple:
            instructions, *validation_keys = input
        else:
            instructions = input
            validation_keys = []

        validation_keys = validation_keys[0] if validation_keys else []
        system_message = Message(role="system",content=instructions)
        user_message = Message(role="user",content=self.user_question)

        if history:
            messages.append(system_message)
            chat_history = self.get_conversation_history()
            for message in chat_history:
                messages.append(Message(role=message.role, content=message.message))
            messages.append(user_message)
        else:
            messages = [system_message, user_message]
        return messages, validation_keys

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
            print(f"Error saving considerations: {e}")
            return e
            
    def run_llm(self, prompt, expected_json = [], name = None):
        try:
            chat = self.azure_llm_client.chat(prompt, True)
            formatted_response = self._format_json(chat)
            print("LLM RESPONSE:", formatted_response)
            if expected_json != [] and not self.validate_json(formatted_response, expected_json):
                raise ValueError("Unexpected JSON response from LLM")
            self.response_pool.put({name:formatted_response})
            self.retry_count = 0
        except Exception as e:
            print("Error querying LLM - retrying..." + str(e))
            if self.retry_count < 2:
                self.retry_count += 1
                self.run_llm(prompt, expected_json)
            else:
                return "Error querying LLM"
            

    def update_conversation_history(self, responses):

        def create_message_content(role, message):
            return MessageContent(role=role, message=message)
        
        def create_raw_chat_message(messages):
            return RawChatMessage(user_session_id=self.user_session, message=messages)

        def assemble_messages():

            for response in responses:
                if response.get('rag_response'):
                    rag = response.get('rag_response').get('response')
                if response.get('kickback_response'):
                    follow_up = response.get('kickback_response').get('follow_up_question')
            full_response = rag if rag + follow_up else "I'm sorry, I'm having trouble understanding your question.  Can you provide more information?"
            messages = [
                create_message_content('user', self.user_question),
                create_message_content('system', full_response)
            ]
            return messages
        
        messages = assemble_messages()
        raw_chat_message = create_raw_chat_message(messages)
        raw_chat_message.save()
        
        self.conversation.history.append(raw_chat_message)
        self.conversation.save()

    def check_considerations(self):
        # first check the users answer to see if any new considerations are revealed
        self.thread_pool['all_consideration_thread'].join()
        classification_prompt, classification_json = self.create_prompt_template(
            get_gpt_classification_prompt(self.all_considerations, json.dumps(self.user_considerations)))
        new_considerations_thread = Thread(target=self.run_llm, args=(classification_prompt, classification_json,"new_considerations"))
        new_considerations_thread.start()
        self.thread_pool['new_considerations_thread'] = new_considerations_thread
        return 


    def full_response(self):

        user_context = self.get_user_context()

        rag = Thread(target=self.run_rag, args=(user_context,))
        rag.start()
        self.thread_pool['rag_thread'] = rag

        self.get_initial_graph()
        self.thread_pool['topic_thread'].join()
        self.run_graph_info()
    
        self.check_considerations()
        self.thread_pool['new_considerations_thread'].join()

        considerations_response = self.response_pool.get()
        if considerations_response.get('contains considerations') == 'yes':
            try_update = self.update_considerations(self.response_pool.get())
            if not try_update:
                print("Error updating user considerations")
            
        user_context = self.get_user_context()

        self.thread_pool['rag_thread'].join()

        rag_prompt, _ = self.create_prompt_template(
            gpt_qa_prompt(user_context, self.rag_response),True)
        kickback_prompt, kickback_json = self.create_prompt_template(
            kick_back_prompt(self.user_question, user_context, self.missing_considerations))
        
        self.thread_pool['graph_consideration_thread'].join()
        self.match_profile_to_graph()
        
        # process rag and follow up question in parallel
        rag_thread = Thread(target=self.run_llm, args=(rag_prompt,[],"rag_response"))
        kickback_thread = Thread(target=self.run_llm, args=(kickback_prompt,kickback_json,"kickback_response"))
        rag_thread.start()
        kickback_thread.start()

        rag_thread.join()
        kickback_thread.join()
        responses = []
        try:
            while not self.response_pool.empty():
                item = self.response_pool.get_nowait()
                item_key = None
                if type(item) == dict:
                    item_key = next(iter(item))  # Or q.get(block=False)
                if item_key == 'rag_response':
                    responses.append(item)
                if item_key == 'kickback_response':
                    responses.append(item)
                yield {"event": item_key, "data": json.dumps({'message' : item[item_key]})}
        except Empty: 
            print('Queue is empty')
        finally:
            self.update_conversation_history(responses)
            yield {"event": "risks", "data": json.dumps({'message': self.risks})}
            yield {"event": "opportunities", "data": json.dumps({'message': self.opportunities})}
            yield {"event": "stream-ended", "data": json.dumps({'stream-ended': 'true'})}

            if self.finder:
                self.finder.close()

            if self.mongo_client:
                self.mongo_client.close()
    
if __name__ == "__main__":

    from pathlib import Path

    relative_path = Path('./app/data/mock_user_session.json')


    with relative_path.open(mode='r') as file:
        mock_user_session : UserSession = UserSession(**json.load(file))
    
    mock_conversation = Conversation(id="65cd0b42372b404efb9805f6", user_id=USER_ID)

    follow_up = FollowUp(USER_QUESTION, mock_user_session, mock_conversation)
    follow_up.full_response()
