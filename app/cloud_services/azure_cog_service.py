
import dotenv, os, copy
dotenv.load_dotenv()
from azure.core.credentials import AzureKeyCredential
from abc import ABC, abstractmethod
from azure.search.documents.aio import SearchClient
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from langchain_community.vectorstores.azuresearch import AzureSearch
from cloud_services.llm_services import get_llm_client, AzureLLMClients
from typing import List

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
        
        
        self.langchain_search_client =  AzureSearch(
        azure_search_endpoint=search_endpoint,
        azure_search_key=search_api_key,
        index_name=index_name,
        embedding_function=self.llm_client.embed_to_array
    )
        
    def getSearchClient(self):
        return self.langchain_search_client
    
    def doc_search(self, text, k=10):
        return self.langchain_search_client.similarity_search(text, k)
    
    def upload(self, text):
        result = self.azure_search_client.upload_documents(text)
        return result
    
    def text_search(self, text):
        results = []
        result = self.azure_search_client.search(text)
        for res in result:
            results.append(res["content"])
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
        
        results = {}
        content_list = []
        q_list = []
        fu_list = []

        def ensure_unique(content, content_set: List):
            if content is not None and content not in content_set:
                content_set.append(content)

        for res in result:

            results = [
                [res.get("content", None),
                 content_list],
                [res.get("questions", None),
                 q_list],
                 [res.get("followups", None),
                  fu_list]
            ]
            for r in results:
                ensure_unique(r[0],r[1])

        return content_list[:2], q_list[:2], fu_list[:2]

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