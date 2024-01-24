import dotenv
dotenv.load_dotenv()

import threading
import cloud_services.llm_services as llm
import os, openai
from typing import List
from cloud_services.openai_response_objects import Message, ChatCompletion
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
OPENAI_ENDPOINT= os.getenv("OPENAI_ENDPOINT")
OPENAI_DEPLOYMENT = os.getenv("DEPLOYMENT_NAME")
OPENAI_MODEL = os.getenv("MODEL_NAME")
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


class SyntheticQnA(FileLogger):
    def __init__(self,document_directory, visited_log, rejected_log, unprocessed_directory):
        super().__init__(document_directory, visited_log, rejected_log, unprocessed_directory)
        self.azure_llm = llm.get_llm_client(api_type='azure',
                                api_version=OPENAI_VERSION,
                                endpoint=OPENAI_ENDPOINT,
                                model=OPENAI_MODEL,
                                deployment=OPENAI_DEPLOYMENT,
                                embedding_deployment=EMBEDDING_DEPLOYMENT)
        self.lock = threading.Lock()
        
        self.prefix_whitelist = [
            "www",
            "www.housing",
            "scai.sdes",
            "registrar",
            "www.fp",
            "guides",
            "www.ehs",
            "cdl",
            "digitallearning",
            "graduate",
            "undergrad",
            "varc.sdes",
            "rwc.sdes",
            "academicsuccess",
            "career"
        ]

    def query_ai(self, messages: List[Message]): 
        return self.azure_llm.chat(messages)
    
    def refresh_client(self):
        with self.lock:
            self.azure_llm = llm.get_llm_client(api_type='azure',
                            api_version=OPENAI_VERSION,
                            endpoint=OPENAI_ENDPOINT,
                            model=OPENAI_MODEL,
                            deployment=OPENAI_DEPLOYMENT,
                            embedding_deployment=EMBEDDING_DEPLOYMENT)
    
    def reset_processed(self):
        self.file_list = [file for file in os.listdir(self.directory) if file.endswith('.json')]
        self.visited = set()
        for file in self.file_list:
            self.visited.add(file)
    
    def generate_completion(self, context_str: list) -> str:
        
        def get_prompt():
            user_content =(
r"""the contents below are scraped from a webpage.  Read the contents from the perspective of a university student"""
r"""and come up with some questions, answers and derived follow up questions, that might represent an FAQ on the content. """
r""" Use keywords and topics in the question and response text as much as possible, as this will improve search results downstream."""
r""" Do not answer the derived follow-up questions, just brainstorm some potential further avenues for exploration."""
r"""Your response MUST BE valid json and should look similar to the structure below, which is included for illustration purposes. """
r"""{ """
r"""    "Topics": [ """
r"""        "Student Learning and Academic Success","""
r"""        "Academic Services","""
r"""        "PeerKnight Coaching Program","""
r"""        "Student Resources","""
r"""    ], """
r"""    "Questions": {"""
r"""        "What is the Division of Student Learning and Academic Success?": "The Division of Student Learning and Academic Success helps undergraduates unleash their full potential and engage in educational and co-curricular opportunities.","""
r"""        "What are the academic planning tools offered?": "Academic planning tools include myKnight Audit, myKnight STAR, mySchedule Builder, and Pegasus Path." """
r"""    }, """
r"""    "Follow-up Questions": [""" 
r"""        "What are the obligations of PeerKnight Coaching Program participants?","""
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
                qna = json.loads(result.content)
                merged_data = {**docs, **qna}
                self.save_json(merged_data, filename)
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
                    self.save_visited_urls()
                    break  # Break on other types of errors

            
    def run_qna(self):
        self.get_docs_to_process()
        self.read_page_content_and_enqueue()
        self.reset_processed()
        
        threads = []
        max_threads = 15  # be careful of rate limiting and CPU usage
        
        
        try:
            while not self.docs.empty() or any(thread.is_alive() for thread in threads):
                # process completed threads:
                for thread in threads:
                    if not thread.is_alive():
                        thread.join()
                
                threads = [thread for thread in threads if thread.is_alive()]
                
                if len(threads) < max_threads :
                    doc, filename = self.docs.get(block=False)
                    filename_pre = self.extract_prefixes(filename)
                    if (filename not in self.visited
                    and filename not in self.rejected
                    and filename not in self.file_list
                    and filename_pre in self.prefix_whitelist
                    ):
                        self.visited.add(filename)
                        self.save_visited_urls()
                        content = doc.get('page_content')
                        content = remove_duplicate_passages(content)
                        
                        thread = threading.Thread(target=self.threaded_generate_completion, args=(content, filename, doc))
                        thread.start()
                        threads.append(thread)

        except KeyboardInterrupt:  
            print("program interrupted, saving urls")  
            self.save_visited_urls()
        except Exception as e: 
            self.save_visited_urls()
        
        self.save_visited_urls()
                

        
    
if __name__ == "__main__":
    prompt = SyntheticQnA(DOCUMENT_DIRECTORY, VISITED_LOG, REJECTED_LOG, UNPROCESSED_DIRECTORY)
    prompt.run_qna()
    
    