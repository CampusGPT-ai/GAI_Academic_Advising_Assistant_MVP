import dotenv
dotenv.load_dotenv()

import threading
from llm_services import AzureLLMClients, get_llm_client
import os, openai
from typing import List
from openai_response_objects import Message, ChatCompletion

# setup openai connection
import logging, sys, json
from file_tracker import FileLogger
from file_utilities import remove_duplicate_passages
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
OPENAI_ENDPOINT= os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_DEPLOYMENT = os.getenv("GPT35_DEPLOYMENT_NAME")
OPENAI_MODEL = os.getenv("GPT35_MODEL_NAME")
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
r"""the contents below are scraped from a webpage.  Read the contents from the perspective of a university student"""
r"""and come up with some questions, answers and derived follow up questions, that might represent an FAQ on the content. """
r""" Use keywords and topics in the question and response text as much as possible, as this will improve search results downstream."""
r""" Do not answer the derived follow-up questions, just brainstorm some potential further avenues for exploration."""
r"""Your response MUST BE valid json and should look similar to the structure below. """
r"""The example below is only for illustration purposes, do NOT use this exact text in your response. """
r"""{ """
r"""    "Topics": [ """
r"""        "Student Learning and Academic Success","""
r"""        "Academic Services","""
r"""        "Peer Coaching Program","""
r"""        "Student Resources","""
r"""    ], """
r"""    "Questions": {"""
r"""        "What is the Division of Student Learning and Academic Success?": "The Division of Student Learning and Academic Success helps undergraduates unleash their full potential and engage in educational and co-curricular opportunities.","""
r"""        "What are the academic planning tools offered?": "Academic planning tools include..." """
r"""    }, """
r"""    "Follow-up Questions": [""" 
r"""        "What are the obligations of peer tutors?","""
r"""        "What kind of assistance does the university provide in terms of study skills?","""
r"""        "How do the mentioned academic planning tools work?" """
r"""    ] """
r""" } """
r"""\n\n"""
r""" [SCRAPED WEBPAGE CONTENTS]: """
f"""{context_str}"""
            )
            return (
                [
            Message(role='system', content=SYSTEM_TEXT),
            Message(role='user',content=user_content)
        ]
            )
    
        
        messages = get_prompt()
        result : ChatCompletion = self.azure_llm.chat(messages)
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
                qna = json.loads(result_content)
                merged_data = {**docs, **qna}
                self.save_json(merged_data, filename, 'index-processed-v2')
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

    async def upload_files(self):
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
    loop.run_until_complete(loader.upload_files())
    loop.close
    
    