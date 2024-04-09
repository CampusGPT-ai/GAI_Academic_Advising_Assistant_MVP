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
    
    def refine_questions(self, user_info, input):
        prompt = get_questions_prompt(user_info, input)
        default_messages = [
            Message(role='system', content=prompt),
            ]
        result : ChatCompletion = self.azure_llm.chat(default_messages)
        result_split = self.split_questions(result.choices[0].message.content)
        return result_split
    
    def generate_questions(self, user_info):
         #search_string = self.get_search_string(user_info)
         results = self.retrieve_content(user_info, n=10)
         result = self.refine_questions(user_info, results['questions'])
         return result
    
    def generate_content_and_questions(self, query, user_info):
         search_string = self.get_keyword_string(query, user_info)
         content = self.retrieve_content(search_string, n=10)
         refined_qs = self.refine_questions(user_info, content['followups'])
         return content, refined_qs
    
    @classmethod           
    def with_default_settings(cls, model_num='GPT35'):
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
                                                settings.SEARCH_INDEX_NAME,
                                                azure_llm,
                                                settings.SEARCH_API_KEY),
        )

    
if __name__ == "__main__":
    retriever = SearchRetriever.with_default_settings()
    retriever4= SearchRetriever.with_default_settings()
    from pathlib import Path

    file_path = Path('app/data/test_user.json')
    with open(file_path, 'r') as f:
        data = json.load(f)

    user_info = json.dumps(data)
    logger.info(retriever.generate_questions(user_info))
