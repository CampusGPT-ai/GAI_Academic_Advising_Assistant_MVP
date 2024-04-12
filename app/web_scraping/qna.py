import dotenv, re
dotenv.load_dotenv()

import threading
from cloud_services.llm_services import AzureLLMClients, get_llm_client
import os, openai
from typing import List
from cloud_services.openai_response_objects import Message, ChatCompletion

# setup openai connection
import logging, sys, json
from web_scraping.file_tracker import FileLogger
from web_scraping.file_utilities import remove_duplicate_passages
import time 
from data.models import kbDocument, WebPageDocument
from settings.settings import Settings
from mongoengine import connect
from web_scraping.scraping_prompts import summarize_chunks
import queue 

settings = Settings()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout)  # Ensures logs go to stdout
    ]
)


OPENAI_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_VERSION = os.getenv("OPENAI_API_VERSION")
OPENAI_ENDPOINT= os.getenv("AZURE_ENDPOINT")
OPENAI_DEPLOYMENT = os.getenv("GPT4_DEPLOYMENT_NAME")
OPENAI_MODEL = os.getenv("GPT4_MODEL_NAME")
EMBEDDING = os.getenv("EMBEDDING")
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_API_KEY= os.getenv("SEARCH_API_KEY")
SEARCH_INDEX_NAME=os.getenv("SEARCH_INDEX_NAME")
SYSTEM_TEXT = '''You are an academic advisor creating an FAQ from your university's website'''
EMBEDDING_DEPLOYMENT = os.getenv("EMBEDDING")

openai.api_key = OPENAI_KEY
openai.api_version = OPENAI_VERSION
openai.base_url = OPENAI_ENDPOINT
openai.azure_endpoint = ''
openai.api_type = 'azure'

UNPROCESSED_DIRECTORY = 'C:\\repos\\isupportu-\\docs2'
DOCUMENT_DIRECTORY = 'C:\\repos\\isupportu-\\QnA'
VISITED_LOG = 'C:\\repos\\isupportu-\\QnA\\logs\\visited.txt'
REJECTED_LOG = 'C:\\repos\\isupportu-\\QnA\\logs\\rejected.txt'

AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
AZURE_STORAGE_ACCOUNT_CRED = os.getenv("AZURE_STORAGE_ACCOUNT_CRED")
AZURE_STORAGE_CONTAINER=os.getenv("AZURE_STORAGE_CONTAINER")

account_url = f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net"

class SyntheticQnA(FileLogger):
    def __init__(self, visited_log, rejected_log, credentials, account_url):
        super().__init__( visited_log, rejected_log, credentials, account_url)
        self.azure_llm = get_llm_client(api_type='azure',
                                api_version=OPENAI_VERSION,
                                endpoint=OPENAI_ENDPOINT,
                                model=OPENAI_MODEL,
                                deployment=OPENAI_DEPLOYMENT,
                                embedding_deployment=EMBEDDING_DEPLOYMENT)
        self.lock = threading.Lock()
        self.threads = []
        self.prefix_whitelist = []
        self.mongo_docs = queue.Queue()

    def query_ai(self, messages: List[Message]): 
        return self.azure_llm.chat(messages)
    
    def refresh_client(self):
        with self.lock:
            self.azure_llm = get_llm_client(api_type='azure',
                            api_version=OPENAI_VERSION,
                            endpoint=OPENAI_ENDPOINT,
                            model=OPENAI_MODEL,
                            deployment=OPENAI_DEPLOYMENT,
                            embedding_deployment=EMBEDDING_DEPLOYMENT)
    
    def generate_completion(self, context_str: list) -> str:
        
        def get_prompt():
            return summarize_chunks(context_str)
    
        
        messages = get_prompt()
        result : ChatCompletion = self.azure_llm.chat(messages)
        print(result.choices[0].message)
        return result.choices[0].message 

    def parse_json(self, json_data):
        output = []

        for qna_item in json_data.get("qna", []):
            dict_item = kbDocument(
                source = json_data.get("metadata", {}).get("source", ""),
                updated = json_data.get("metadata", {}).get("last_updated", ""),
                text = qna_item
            )
            output.append(dict_item)

        return output

    def extract_prefixes(self,filename):
        parts = filename.split('.ucf.edu')[0]
        return parts

    def threaded_generate_completion(self, content, filename, docs):
        max_retries = 3  # Maximum number of retries
        retry_delay = 10  # Delay in seconds

        for attempt in range(max_retries):
            try:
                print(f"adding {filename} to a thread (Attempt {attempt + 1})")
                result = self.generate_completion(content)
                print(f"Completed QnA for {filename}")
                result_content = result.content.replace(r"```","").replace("json","")
                result_content = {"qna": re.split('\n\n---\n\n|\n\n', result_content)}
                merged_data = {**docs, **result_content}
                output = self.parse_json(merged_data)
                for o in output:
                    try:
                        o.save()
                        print(f"Saved to MongoDB")
                    except Exception as e:
                        raise e

                break  # Break out of the loop if successful
            except Exception as e:
                print(f"Error querying GPT for {filename}: {e}")

                # Check if the error is related to rate limiting
                if "rate limit" in str(e).lower() or "429" in str(e):
                    print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                elif "Unauthorized" in str(e):
                    self.refresh_client()
                elif "Invalid" in str(e):
                    next
                else:
                    self.rejected.add(filename)
                    self.visited.add(filename)
                    break  # Break on other types of errors

    async def chunked_files(self):
        self.threads = []
        max_threads = 15 # be careful of rate limiting and CPU usage
                #start consumer thread production
        for _ in range(max_threads):
            thread = threading.Thread(target=self.run_qna)
            thread.start()
            self.threads.append(thread)
        
        self.get_docs_from_mongo()

        # replaced with mongo - can clean up later
        #await self.get_docs_to_process("index-upload")
        # start producing docs in the queue
        #await self.read_page_content_and_enqueue("index-upload")

        for _ in self.threads: 
            self.mongo_docs.put(None)

        for thread in self.threads:
            thread.join()

    @staticmethod
    def find_document_by_source_and_updated(source, updated):
        # Query for a document with the given source and updated time
        document = kbDocument.objects(source=source, updated=updated).first()
        
        if document:
            return True
        else:
            return False
        
    def get_docs_from_mongo(self):
        documents = WebPageDocument.objects.all()
        for doc in documents:
            json_doc = doc._data
            self.mongo_docs.put(json_doc)

    def run_qna(self):
        while True:
            doc = self.mongo_docs.get()
            doc['metadata'] = doc.get('metadata')._data
            metadata = doc.get('metadata')

            if self.find_document_by_source_and_updated(metadata.get('source'), metadata.get('last_updated')):
                continue

            if doc is None:
                continue

            filename = metadata.get('source')

            max_retries = 3  # Maximum number of retries
            retry_delay = 10  # Delay in seconds
            for attempt in range(max_retries):
                try:
                    # process completed threads:

                    self.visited.add(filename)
                    # self.save_visited_urls()
                    content = doc.get('page_content')
                    content = remove_duplicate_passages(content)
                    self.threaded_generate_completion(content,filename,doc)

                except KeyboardInterrupt:  
                    print("program interrupted, saving urls")  
                    #self.save_visited_urls()
                except Exception as e: 
                    logging.info(f"exception from qna {str(e)}")
                    #self.save_visited_urls( )
                
                #self.save_visited_urls()
                

        
    
if __name__ == "__main__":
    db_name = settings.MONGO_DB
    db_conn = settings.MONGO_CONN_STR
    _mongo_conn = connect(db=db_name, host=db_conn)
    import asyncio
    loop = asyncio.get_event_loop()
    loader = SyntheticQnA("visited.txt","rejected.txt", credentials=AZURE_STORAGE_ACCOUNT_CRED, account_url=account_url)
    loop.run_until_complete(loader.chunked_files())
    loop.close
    _mongo_conn.close()
    
    