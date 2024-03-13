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
            user_content =(
r"""You are an NLP agent.  Your job is to convert raw text into semantic search strings.  \n\n
For the text below identify facts about people, places, entities, events, advice, recommendations, actions, or any other topics you can think of.  \n
For each fact you find, list the fact in a short paragraph.  \n
- The paragraph should include the fact itself and all additional context that will help improve semantic search results using cosign similarity search on the embedded data. \n
- Each paragraph should stand alone, without relying on knowledge of preceeding text to make sense. \n  
- Repeat major topics, themes, and other facts from the body of the text for each paragraph. \n
Create as many paragraphs for as many facts as you possibly can.  \n
always include specific dates if they are provided. \n
Always include addresses and contact information if it is provided.  \n
Do not number the paragraphs.  Separate each paragraph with a double line break.  """
r"""\n\n"""
r""" [SCRAPED WEBPAGE CONTENTS]:\n """
f"""{context_str}\n\n"""
            )
            return (
                [
            Message(role='system', content=SYSTEM_TEXT),
            Message(role='user',content=user_content)
        ]
            )
    
        
        messages = get_prompt()
        result : ChatCompletion = self.azure_llm.chat(messages)
        print(result.choices[0].message)
        return result.choices[0].message  
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
                self.save_json(merged_data, filename, 'index-short-text')
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

        await self.get_docs_to_process("index-upload-v2")
        # start producing docs in the queue
        await self.read_page_content_and_enqueue("index-upload-v2")

        for _ in self.threads: 
            self.docs.put((None,None))

        for thread in self.threads:
            thread.join()


    def run_qna(self):
        while True:
            doc, filename = self.docs.get()

            if doc is None and filename is None:
                break

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
    import asyncio
    loop = asyncio.get_event_loop()
    loader = SyntheticQnA("visited.txt","rejected.txt", credentials=AZURE_STORAGE_ACCOUNT_CRED, account_url=account_url)
    loop.run_until_complete(loader.chunked_files())
    loop.close
    
    