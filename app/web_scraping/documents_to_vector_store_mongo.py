import uuid
import os, time, threading
from dotenv import load_dotenv
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from web_scraping.file_tracker import FileLogger
import web_scraping.llm_services as llm
from web_scraping.azure_cog_service import AzureSearchService
from datetime import datetime
import pytz
from azure.storage.blob.aio import BlobServiceClient
from web_scraping.file_utilities import remove_duplicate_passages
import copy
from settings.settings import Settings
settings = Settings()
from mongoengine import connect, disconnect
import mongoengine.connection
from data.models import kbDocument, indexDocument

db_name = settings.MONGO_DB
db_conn = settings.MONGO_CONN_STR
load_dotenv()


OPENAI_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_VERSION = os.getenv("OPENAI_API_VERSION")
OPENAI_ENDPOINT= os.getenv("AZURE_ENDPOINT")
OPENAI_DEPLOYMENT = os.getenv("DEPLOYMENT_NAME")
OPENAI_MODEL = os.getenv("MODEL_NAME")
EMBEDDING = os.getenv("EMBEDDING")
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_API_KEY= os.getenv("SEARCH_API_KEY")
SEARCH_INDEX_NAME=os.getenv("SEARCH_INDEX_NAME")
SYSTEM_TEXT = '''You are an academic advisor creating an FAQ from your university's website'''
EMBEDDING_DEPLOYMENT = os.getenv("EMBEDDING")
MAX_TOKEN_LENGTH = 6000
BATCH_SIZE = 100
AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
AZURE_STORAGE_ACCOUNT_CRED = os.getenv("AZURE_STORAGE_ACCOUNT_CRED")
AZURE_STORAGE_CONTAINER=os.getenv("AZURE_STORAGE_CONTAINER")

account_url = f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net"

class VectorUploader():
    def __init__(self):
        self.azure_llm = llm.get_llm_client(api_type='azure',
                                api_version=OPENAI_VERSION,
                                endpoint=OPENAI_ENDPOINT,
                                model=OPENAI_MODEL,
                                deployment=OPENAI_DEPLOYMENT,
                                embedding_deployment=EMBEDDING_DEPLOYMENT)
        
        self.search_client = AzureSearchService(SEARCH_ENDPOINT,
                                                SEARCH_INDEX_NAME,
                                                self.azure_llm,
                                                SEARCH_API_KEY)

    def refresh_client(self):
        self.azure_llm = llm.get_llm_client(api_type='azure',
                                api_version=OPENAI_VERSION,
                                endpoint=OPENAI_ENDPOINT,
                                model=OPENAI_MODEL,
                                deployment=OPENAI_DEPLOYMENT,
                                embedding_deployment=EMBEDDING_DEPLOYMENT)
        
        self.search_client = AzureSearchService(SEARCH_ENDPOINT,
                                                SEARCH_INDEX_NAME,
                                                self.azure_llm,
                                                SEARCH_API_KEY)
        
    def check_upload_status(self):
        documents_already_processed = set()
        for doc in indexDocument.objects():  # Query all documents
            documents_already_processed.add(doc.content)
        return documents_already_processed

    def upload_files(self):
        _mongo_conn = connect(db=db_name, host=db_conn)
        retry_delay = 10
        docs_to_upload = []
        processed_docs = []
        batch_size = BATCH_SIZE
        indexed_docs = self.check_upload_status()
        try:
            for doc in kbDocument.objects():
                if doc.text in indexed_docs:
                    # print(f"Document already indexed: {doc.text}")
                    continue
                try:
                    doc_processed = self.json_to_index(doc)
                    if len(docs_to_upload) >= batch_size:
                        results = self.search_client.upload(docs_to_upload)
                        is_error = False
                        for result in results:
                            if not result.succeeded:
                                print(f"Failed to upload document: {result.key}")
                                is_error = True
                        if not is_error: 
                            #update list of processed docs
                            processed_docs.extend(docs_to_upload) #make copy of search index offline
                            print(f"Document uploaded successfully: {len(docs_to_upload)}")
                        docs_to_upload = []
                    else:
                        docs_to_upload.append(doc_processed)

                except Exception as e:
                    if "Unauthorized" in str(e):
                        self.refresh_client()
                    if "rate limit" in str(e).lower() or "429" in str(e):
                        print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        print(f"exception logged for {str(e)}") 
                finally:
                    next
        except Exception as e:
            print(f"exception logged for {str(e)}")
        finally:
            processed_docs = self.index_to_doc(processed_docs)
            if processed_docs:
                for doc in processed_docs:
                    doc.save() 
            disconnect()
    
    # convert list of json strings to mongo documents
    def index_to_doc(self, json_data):
        output = []

        for item in json_data:
            dict_item = indexDocument(
                vector_id = item.get("id", str(uuid.uuid4())),
                source = item.get("source", ""),
                last_updated = item.get("last_updated", ""),
                content = item.get("content", ""),
                content_vector = item.get("content_vector", None),
            )
            output.append(dict_item)

        return output
                        
        
    def embed(self, text):
        try:
            result = self.azure_llm.embed_to_array(text)
        except Exception as e:
            if "rate limit" in str(e).lower() or "429" in str(e):
                print(f"Rate limit exceeded. Retrying in 20 seconds...")
                time.sleep(20)
            else: 
                raise e
        return result
    


    def convert_to_edm_datetimeoffset(self, date_string):
        dt = datetime.fromisoformat(date_string)
        dt = dt.replace(tzinfo=pytz.UTC)
        edm_datetimeoffset = dt.isoformat()
        return edm_datetimeoffset
        
    
    def json_to_index(self, document):
        
        try:
            index_document = {
            "@search.action": "upload",
            "id": str(uuid.uuid4()),
            "content": document["text"],
            "last_updated": self.convert_to_edm_datetimeoffset(document["updated"]),
            "source": document["source"],
            "content_vector": self.embed(document["text"]),
            #Add other fields as required by your index schema
            }
        except:
            raise Exception("unable to parse json document due to malformed text")
        
        return index_document
    
if __name__ == "__main__":
    loader = VectorUploader()
    loader.upload_files()
    print("Upload complete")

            


