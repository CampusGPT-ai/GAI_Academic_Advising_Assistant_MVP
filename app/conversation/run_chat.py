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
from threading import Thread
from cloud_services.internet_search import query_google
import json
from queue import Queue, Empty
from data.models import ConversationSimple as Conversation, MessageContent, RawChatMessage, UserSession
import logging
logger = logging.getLogger(__name__)
settings = Settings()

USER_QUESTION = "What types of courses should I take to gain more knowledge in robotics"
USER_ID = "A_iXG9LQjG86PTY1sgG-Sm9JO3IbMlliRkZok3BhT8I"
#will just proxy this for testing (this will be a route)

class QueryLLM:
    def __init__(self, user_session: UserSession, user_info, model=settings.GPT4_MODEL_NAME, deployment=settings.GPT4_DEPLOYMENT_NAME):
        self.model = model
        self.deployment = deployment
        self.user_info = user_info
        self.user_session = user_session
        self.user_id = user_session.user_id


        self.azure_llm_client = get_llm_client(api_type='azure',
                                                api_version=settings.OPENAI_API_VERSION,
                                                endpoint=settings.AZURE_OPENAI_ENDPOINT,
                                                model=self.model,
                                                deployment=self.deployment,
                                                embedding_deployment=settings.EMBEDDING)
        
        
        self.retry_count = 0

        self.response_pool = Queue()

    
    # check for the existence of a key in a dictionary, to validate that the LLM response returned the expected JSON
    # should probably move this to the LLM service as it is common to all LLM JSON responses


    def create_prompt_template(self, input, history=[], user_question=None):
        messages = []
        user_message = None

        if type(input) == tuple:
            instructions, *validation_keys = input
            validation_keys = validation_keys[0] if validation_keys else []
        else:
            instructions = input
            validation_keys = []

        system_message = Message(role="system",content=instructions)
   
        messages.append(system_message)

        if history != []:
            for message in history:
                message_data = message._data['message']
                for m in message_data:
                    messages.append(Message(role=m.role, content=m.message))
       
        if user_question:
            user_message = Message(role="user",content=user_question)
            messages.append(user_message)

        return messages, validation_keys

            
    def run_llm(self, prompt, expected_json = []):
        try:
            chat = self.azure_llm_client.chat(prompt, True)
            formatted_response = self.azure_llm_client._format_json(chat)
            if expected_json != [] and not self.azure_llm_client.validate_json(formatted_response, expected_json):
                raise ValueError("Unexpected JSON response from LLM")
            return formatted_response
        except Exception as e:
            print("Error querying LLM - retrying..." + str(e))
            if self.retry_count < 2:
                self.retry_count += 1
                self.run_llm(prompt, expected_json)
            else:
                return "Error querying LLM"
            
    
if __name__ == "__main__":
    pass