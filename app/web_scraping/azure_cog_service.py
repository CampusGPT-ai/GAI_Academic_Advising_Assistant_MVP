
import logging
import dotenv, os, copy
dotenv.load_dotenv()
from azure.core.credentials import AzureKeyCredential
from abc import ABC, abstractmethod
from azure.search.documents.aio import SearchClient
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from cloud_services.llm_services import get_llm_client, AzureLLMClients
from typing import List

logger = logging.getLogger(__name__)

class VectorSearchService(ABC):
    @abstractmethod
    def getSearchClient(self):
        pass

class AzureSearchService(VectorSearchService):
    def __init__(self, 
                 search_endpoint: str,
                 index_name: str,
                 llm_client : AzureLLMClients,
                 search_api_key: str):
        
        self.llm_client = llm_client
        self.search_credential = AzureKeyCredential(search_api_key)
                
        self.azure_search_client = SearchClient(endpoint=search_endpoint,
                                   index_name=index_name,
                                   credential=self.search_credential)
        
        
       
    def getSearchClient(self):
        return self.azure_search_client
    
    def upload(self, documents: List[dict]):
        if not isinstance(documents, list):
            raise ValueError("Documents must be a list of dictionaries")
        result = self.azure_search_client.upload_documents(documents)
        return result
    
    def text_search(self, text):
        results = []
        result = self.azure_search_client.search(text)
        for res in result:
            results.append(res["content"])
        return results
    
    @staticmethod
    def dedup_results(result,key):
        results=[]
        for res in result:
            id = res[key]
            if results == []:
                results.append(res)
            else:
                results_id_list = [result[key] for result in results if key in result]
                if id not in results_id_list:
                    results.append(res)

        return results
    
    def simple_search(self, text, vector_field, n=3):
        vector_query = VectorizedQuery(
        vector=self.llm_client.embed_to_array(text),
            k_nearest_neighbors=n,
            fields=vector_field
        )
                # Search Query

        result = self.azure_search_client.search(
            vector_queries=[vector_query]
            )
        
        results = self.dedup_results(result,"content")
        return results

    def hybrid_search(self, text, vector_field: List[str], n):
        vqs = []
        for field in vector_field:
            vector_query = VectorizedQuery(
            vector=self.llm_client.embed_to_array(text),
                k_nearest_neighbors=n,
                fields=field
            )
            vqs.append(vector_query)
                    # Search Query

        result = self.azure_search_client.search(
            search_text=text,
            vector_queries=vqs)
        results = []
        for res in result:
            results.append(res["content"])
        return results

if __name__ == "__main__":
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    OPENAI_API_KEY = os.getenv
    OPENAI_VERSION = os.getenv("OPENAI_API_VERSION")
    OPENAI_ENDPOINT= os.getenv("OPENAI_ENDPOINT")
    OPENAI_DEPLOYMENT = os.getenv("DEPLOYMENT_NAME")
    OPENAI_MODEL = os.getenv("MODEL_NAME")
    EMBEDDING_DEPLOYMENT = os.getenv("EMBEDDING")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
    SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
    SEARCH_API_KEY= os.getenv("SEARCH_API_KEY")
    SEARCH_INDEX_NAME=os.getenv("SEARCH_INDEX_NAME")

    llm_client = get_llm_client(api_type='azure',
                                api_version=OPENAI_VERSION,
                                endpoint=OPENAI_ENDPOINT,
                                model=OPENAI_MODEL,
                                deployment=OPENAI_DEPLOYMENT,
                                embedding_deployment=EMBEDDING_DEPLOYMENT)

    search_client = AzureSearchService(search_endpoint=SEARCH_ENDPOINT,
                                       index_name=SEARCH_INDEX_NAME,
                                       llm_client=llm_client,
                                       search_api_key=SEARCH_API_KEY)
    QUERY_TEXT = "what courses are required for a physics degree?"
    VECTOR_FIELD ='content_vector'
    VECTOR_FIELDS  = ['content_vector','questions_vector']
    
    # lanchain cognitive search connector is incompatible with production version of azure search
    # langchain_result = search_client.doc_search(QUERY_TEXT)
    azure_result = search_client.hybrid_search(QUERY_TEXT,VECTOR_FIELDS,1)
    print(azure_result[:2])
