from abc import ABC, abstractmethod
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential
from langchain.embeddings import AzureOpenAIEmbeddings

embeddings = AzureOpenAIEmbeddings(
    azure_deployment="embedding",
    openai_api_version="2023-05-15",
)
from langchain.vectorstores.azuresearch import AzureSearch

     
class VectorSearchService(ABC):
    @abstractmethod
    def getSearchClient(self):
        pass

class AzureSearchService:
    def __init__(self, 
                 endpoint: str,
                 api_key: str,
                 index_name: str):
        
        credential = AzureKeyCredential(api_key)
        self.client = SearchClient(endpoint=endpoint,
                                   index_name=index_name,
                                   credential=credential)


        self.langchain_client =  AzureSearch(
        azure_search_endpoint=endpoint,
        azure_search_key=api_key,
        index_name=index_name,
        embedding_function=embeddings.embed_query,
    )
        
    def getSearchClient(self):
        return self.langchain_client
    
def get_search_client(endpoint: str, api_key: str, index_name: str) -> VectorSearchService:
    return AzureSearchService(
        endpoint=endpoint,
        api_key=api_key,    
        index_name=index_name
    )

