from cloud_services.llm_services import AzureLLMClients, get_llm_client
from settings.settings import Settings
from conversation.prompt_templates.kick_back_prompt import get_gpt_system_prompt as kick_back_prompt
from conversation.prompt_templates.gpt_qa_prompt import get_gpt_system_prompt as gpt_qa_prompt
from conversation.prompt_templates.classify_graph_prompt import get_gpt_classification_prompt
from conversation.prompt_templates.internet_search_query import get_gpt_search_prompt
from cloud_services.openai_response_objects import Message
from cloud_services.connect_mongo import MongoConnection
from threading import Thread
from cloud_services.internet_search import query_google
import json
from mongoengine import Document
from queue import Queue, Empty
from data.models import ConversationSimple as Conversation, MessageContent, RawChatMessage, UserSession
import logging
logger = logging.getLogger(__name__)
settings = Settings()

USER_QUESTION = "What types of courses should I take to gain more knowledge in robotics"
USER_ID = "A_iXG9LQjG86PTY1sgG-Sm9JO3IbMlliRkZok3BhT8I"
#will just proxy this for testing (this will be a route)

class QueryLLM:
    def __init__(self, user_session: UserSession, model=settings.GPT4_MODEL_NAME, deployment=settings.GPT4_DEPLOYMENT_NAME):
        self.model = model
        self.deployment = deployment
        self.user_session = user_session
        self.user_id = user_session.user_id

        self.openai_llm_client : AzureLLMClients = get_llm_client(api_type='openai',
                                                                  api_key=settings.OPENAI_API_KEY,
                                                                  model=settings.OPENAI_DIRECT_MODEL)


        self.azure_llm_client : AzureLLMClients = get_llm_client(api_type='azure',
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

        messages.extend(history)

        if user_question:
            user_message = Message(role="user",content=user_question)
            messages.append(user_message)

        return messages, validation_keys

            
    def run_llm(self, prompt, expected_json = []):
        try:
            #$chat = self.azure_llm_client.chat(prompt, True)
            if settings.OPENAI_API_TYPE=='azure':
                chat = self.azure_llm_client.chat(prompt, True)
            else:
                chat = self.openai_llm_client.chat(prompt, True)

            logger.info(f"run llm returned response from api")
            formatted_response = self.azure_llm_client._format_json(chat)
            final_out = self.azure_llm_client.validate_json(formatted_response, expected_json)
            self.retry_count = 0
            return final_out
        except Exception as e:
            if self.retry_count < 2:
                self.retry_count += 1
                logger.error(f"error returning response from LLM:  {str(e)} \n retrying with retry count at {self.retry_count}")
                return self.run_llm(prompt, expected_json)
            else:
                return Exception("error returning response from llm: ", str(e))

            
    
if __name__ == "__main__":
    from conversation.prompt_templates.gpt_qa_prompt import get_gpt_system_prompt 
    from pathlib import Path


    relative_path = Path('./app/data/mock_user_session.json')
    with relative_path.open(mode='r') as file:
        mock_user_session : UserSession = UserSession(**json.load(file))
    

    prompt = get_gpt_system_prompt(USER_QUESTION,'')
    llm = QueryLLM(mock_user_session)
    template, _ = llm.create_prompt_template(prompt)
    response = llm.run_llm(template)
    print(response)