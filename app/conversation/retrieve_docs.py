from cloud_services.llm_services import get_llm_client, AzureLLMClients
from cloud_services.azure_cog_service import AzureSearchService
import os
import logging
from dotenv import load_dotenv
import re, json
from conversation.prompt_templates.search_string_prompt import get_search_prompt, get_keyword_prompt
from conversation.prompt_templates.refine_questions_prompt import get_questions_prompt
from cloud_services.openai_response_objects import ChatCompletion, Message
from settings.settings import Settings
settings = Settings()
load_dotenv()

logger = logging.getLogger(__name__)

class SearchRetriever:
    def __init__(self, llm_client, search_client):
        self.azure_llm : AzureLLMClients  = llm_client        
        self.search_client : AzureSearchService = search_client
        
    def retrieve_content(self,query: str,n=3 ) -> list:
        results = self.search_client.simple_search(query,settings.KB_FIELDS_CONTENT,n)
        output = self.transpose_dict(results)
        return output
    
    def retrieve_keyword_content(self, query: str, n=3) -> list:
        results = self.search_client.text_search(query, n)
        output = self.transpose_dict(results)
        return output
    
    @staticmethod
    def parse_questions(string):
          questions =  re.findall(r'Question: (.*?)\n', string)
          return questions[:2]
    
    @staticmethod
    def split_questions(text):
        split_text = re.split(r'\n|\?|\d+\.\s*', text)
        cleaned_text = [item.strip()+'?' for item in split_text if item.strip()]
        return cleaned_text
    
    @staticmethod
    def transpose_dict(results_dict):
        keys = results_dict[0].keys()
        transposed = {}
        for key in keys:
            transposed[key] = [d[key] for d in results_dict]

        return transposed
    
    def get_search_string(self, input):
        prompt = get_search_prompt(input)
        default_messages = [
            Message(role='system', content=prompt),
        ]
        result : ChatCompletion = self.azure_llm.chat(default_messages)
        return result.choices[0].message.content
    
    def get_keyword_string(self, input, user_info):
        prompt = get_keyword_prompt(input, user_info)
        default_messages = [
            Message(role='system', content=prompt),
        ]
        result : ChatCompletion = self.azure_llm.chat(default_messages)
        return result.choices[0].message.content
    
    def refine_questions(self, user_info):
        prompt = get_questions_prompt(user_info)
        default_messages = [
            Message(role='system', content=prompt),
            ]
        result : ChatCompletion = self.azure_llm.chat(default_messages, True)
        #  logger.info(f"Refine questions result: {result}")
        result = self.azure_llm._format_json(result)

        result = self.azure_llm.validate_json(result, ['questions'])

        return result
    
    def generate_questions(self, user_info):
         #search_string = self.get_search_string(user_info)
         result = self.refine_questions(user_info)
         logger.info(f"Refined questions: {result}")
         return result
    
    def generate_content_and_questions(self, query, user_info):
         search_string = self.get_keyword_string(query, user_info)
         print('generated search string for keyword search: ', search_string)
         vector_content = self.retrieve_content(search_string, n=10)

         refined_qs = self.refine_questions(user_info, vector_content['followups'])
         return vector_content, refined_qs
    
    @classmethod           
    def with_default_settings(cls, index_name=settings.SEARCH_INDEX_NAME, model_num='GPT35'):
        from cloud_services.llm_services import get_llm_client
        from cloud_services.azure_cog_service import AzureSearchService
        if model_num=='GPT35':
            selected_model = settings.GPT35_MODEL_NAME,
            selected_deployment = settings.GPT35_DEPLOYMENT_NAME
        else:
            selected_model = settings.GPT4_MODEL_NAME,
            selected_deployment = settings.GPT4_DEPLOYMENT_NAME

        azure_llm = get_llm_client(api_type='azure',
                                api_version=settings.OPENAI_API_VERSION,
                                endpoint=settings.AZURE_OPENAI_ENDPOINT,
                                model=selected_model,
                                deployment=selected_deployment,
                                embedding_deployment=settings.EMBEDDING)

        # Create an instance of the class with these default settings
        return cls(
            llm_client=azure_llm,
            search_client=AzureSearchService(settings.SEARCH_ENDPOINT,
                                                index_name,
                                                azure_llm,
                                                settings.SEARCH_API_KEY),
        )

    
if __name__ == "__main__":
    retriever = SearchRetriever.with_default_settings()
    retriever_catalog = SearchRetriever.with_default_settings(index_name=settings.SEARCH_CATALOG_NAME)
    from pathlib import Path
    from mongoengine import connect
    from data.models import UserSession

    USER_QUESTION = 'when is course ENC4290 offered and is it required for computer science majors?'
    relative_path = Path('./app/data/mock_user_session.json')
    with relative_path.open(mode='r') as file:
        mock_user_session : UserSession = UserSession(**json.load(file))

    db_name = os.getenv("MONGO_DB")
    db_conn = os.getenv("MONGO_CONN_STR")
    _mongo_conn = connect(db=db_name, host=db_conn)

    from user.get_user_info import UserInfo
    user_info = json.dumps(UserInfo(mock_user_session.user_id).user_profile.considerations)
    keyword_string = retriever_catalog.get_keyword_string(USER_QUESTION, user_info)
    #print("KEYWORD STRING:", keyword_string)
    #vector_result = retriever_catalog.retrieve_content(USER_QUESTION, n=3)
    #print("NONKEYWORD VECTOR SEARCH:", vector_result.get("content"))
    #vector_keyword_result = retriever_catalog.retrieve_content(keyword_string, n=3)
    #print("KEYWORD VECTOR SEARCH:", vector_keyword_result.get("content"))
    keyword_search = retriever_catalog.retrieve_keyword_content(USER_QUESTION)
    print("TEXT SEARCH:", keyword_search)
    ##keyword_keyword_search = retriever_catalog.retrieve_keyword_content(keyword_string)
    #print("TEXT KEYWORD SEARCH:", keyword_keyword_search)

