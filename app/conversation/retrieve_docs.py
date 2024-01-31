from cloud_services.llm_services import get_llm_client
from cloud_services.azure_cog_service import AzureSearchService
import os
from dotenv import load_dotenv
import re, json
from conversation.search_string_prompt import get_prompt
from conversation.refine_questions_prompt import get_questions_prompt
from cloud_services.openai_response_objects import ChatCompletion, Message

load_dotenv()
# TODO: sub out for settings.py

VECTOR_FIELD = 'content_vector'
VECTOR_FIELDS = ['content_vector']

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_VERSION = os.getenv("OPENAI_API_VERSION")
OPENAI_ENDPOINT= os.getenv("OPENAI_ENDPOINT")
OPENAI_DEPLOYMENT = os.getenv("DEPLOYMENT_NAME")
OPENAI_MODEL = os.getenv("MODEL_NAME")
EMBEDDING = os.getenv("EMBEDDING")
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_API_KEY= os.getenv("SEARCH_API_KEY")
SEARCH_INDEX_NAME=os.getenv("SEARCH_INDEX_NAME")
SYSTEM_TEXT = '''prompt'''
EMBEDDING_DEPLOYMENT = os.getenv("EMBEDDING")



class SearchRetriever:
    def __init__(self):
        self.azure_llm = get_llm_client(api_type='azure',
                                api_version=OPENAI_VERSION,
                                endpoint=OPENAI_ENDPOINT,
                                model=OPENAI_MODEL,
                                deployment=OPENAI_DEPLOYMENT,
                                embedding_deployment=EMBEDDING_DEPLOYMENT)
        
        self.search_client : AzureSearchService = AzureSearchService(SEARCH_ENDPOINT,
                                                SEARCH_INDEX_NAME,
                                                self.azure_llm,
                                                SEARCH_API_KEY)
        
    def retrieve_content(self,query: str) -> list:
            results = self.search_client.simple_search(query,'content_vector',["content"])
            return results[:2]
    
    def retrieve_questions(self, query: str) -> list:
            # could also add "followups"
            results = self.search_client.simple_search(query,'content_vector',["questions"],10)
            get_questions = []
            for i in results:
                  if i.startswith("Question"):
                        print(i)
                        get_questions.append(self.parse_questions(i))
            return get_questions
    
    def parse_questions(self,string):
          questions =  re.findall(r'Question: (.*?)\n', string)
          return questions[:2]
    
    def split_questions(self, text):
        split_text = re.split(r'\n|\?|\d+\.\s*', text)
        cleaned_text = [item.strip() for item in split_text if item.strip()]
        return cleaned_text
    
    def get_search_string(self, input):
        prompt = get_prompt(input)
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
        result = self.split_questions(result.choices[0].message.content)
        return result
    
if __name__ == "__main__":
     retriever = SearchRetriever()
     from pathlib import Path

     file_path = Path('app/data/test_user.json')
     with open(file_path, 'r') as f:
        data = json.load(f)

     user_info = json.dumps(data)
     #print(retriever.retrieve_content("what classes do I need for a BS in physics"))
     search_string = retriever.get_search_string(user_info)
     qs   = retriever.retrieve_questions(search_string)
     print(retriever.refine_questions(user_info, qs))