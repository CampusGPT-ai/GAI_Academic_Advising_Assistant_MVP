import uuid
import os, time, threading
from dotenv import load_dotenv
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from file_tracker import FileLogger
import llm_services as llm
from azure_cog_service import AzureSearchService
from datetime import datetime
import pytz
from azure.storage.blob.aio import BlobServiceClient
from file_utilities import remove_duplicate_passages
import copy

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

AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
AZURE_STORAGE_ACCOUNT_CRED = os.getenv("AZURE_STORAGE_ACCOUNT_CRED")
AZURE_STORAGE_CONTAINER=os.getenv("AZURE_STORAGE_CONTAINER")

account_url = f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net"

class VectorUploader(FileLogger):
    def __init__(self, visited_log, rejected_log, credentials, account_url):
        super().__init__( visited_log, rejected_log, credentials, account_url)
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

    @staticmethod   
    def simple_tokenizer(text):
        # Split the text into tokens based on spaces
        tokens = text.split()
        return tokens
    
    def split_texts(self, doc):
        tokens = self.simple_tokenizer(doc["page_content"])
        length = len(tokens)
        if length > MAX_TOKEN_LENGTH:
            raise Exception("document anomaly detected")
        
        '''split one document into multiple documents with the same metadata tagging'''
        r_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000, chunk_overlap=200,
        separators=[".", "?", "!", ",", " ", ""]
    )
        docs = r_splitter.split_text(
            doc["page_content"])
        new_doc_list = []
        for d in docs:
            new_doc = copy.deepcopy(doc)

            new_doc["page_content"] = d
            new_doc_list.append(new_doc)
            
        return new_doc_list
    
    def get_text_position(self, text):
        return
    
    def threaded_upload(self):
        while True:
            docs, filename = self.docs.get()

            if docs is None and filename is None:
                break

            max_retries = 3  # Maximum number of retries
            retry_delay = 10  # Delay in seconds
            
            try:
                docs = self.split_texts(docs)
            except:
                print(f"document anomaly detected for file {filename}")
                continue

            for attempt in range(max_retries):
                try:
                    print(f"starting upload for {filename}")
                    text = [self.json_to_index(doc) for doc in docs]
                    results = self.search_client.upload(text)
                    is_error = False
                    for result in results:
                        if not result.succeeded:
                            print(f"Failed to upload document: {result.key}")
                            is_error = True
                    if not is_error: 
                        #update list of processed docs
                        print(f"Document uploaded successfully: {filename}")
                        break
                except Exception as e:
                    if "Unauthorized" in str(e):
                        self.refresh_client()
                    if "rate limit" in str(e).lower() or "429" in str(e):
                        print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        print(f"exception logged for {str(e)}") 
                        break        

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

    async def upload_files(self):
        self.threads = []
        max_threads = 15  # be careful of rate limiting and CPU usage
        await self.get_docs_to_process("index-processed")
        
        #start consumer thread production
        for _ in range(max_threads):
            thread = threading.Thread(target=self.threaded_upload)
            thread.start()
            self.threads.append(thread)

        # start producing docs in the queue
        await self.read_page_content_and_enqueue("index-processed")

        for _ in self.threads: 
            self.docs.put((None,None))

        for thread in self.threads:
            thread.join()

                
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
        
        if "title" in document["metadata"]:
            title = document["metadata"]["title"]
        else:
            title = ""
        
        if "Topics" in document:
            keywords = ", ".join(document["Topics"])
        else:
            keywords = ""
        # need more formatting to split question to Q&A    
        if "Questions" in document:
            result = []
            questions = document.get('Questions', {})
            for question, answer in questions.items():
                result.append(f"Question: {question} \n Answer: {answer} \n")

            qna = " ".join(result)
        else:
            qna = ""
            
        if "Follow-up Questions" in document:
            fuq = " ".join(document["Follow-up Questions"])
        else:
            fuq = ""
        
        try:
            index_document = {
            "@search.action": "upload",
            "id": str(uuid.uuid4()),
            "title": title,
            "last_updated": self.convert_to_edm_datetimeoffset(document["metadata"]["last_updated"]),
            "source": document["metadata"]["source"],
            "content": remove_duplicate_passages(document["page_content"]),
            "content_vector": self.embed(document["page_content"]),
            "questions": qna,
            "questions_vector": self.embed(qna),
            "followups": fuq,
            "followups_vector": self.embed(fuq),
            "keywords": keywords
            #Add other fields as required by your index schema
            }
        except:
            raise Exception("unable to parse json document due to malformed text")
        
        return index_document
    
if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loader = VectorUploader("visited.txt","rejected.txt", credentials=AZURE_STORAGE_ACCOUNT_CRED, account_url=account_url)
    loop.run_until_complete(loader.upload_files())
    loop.close
    
    

            


