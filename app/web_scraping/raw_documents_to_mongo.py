from mongoengine import connect, disconnect
from data.models import WebPageDocument, Metadata
import mongoengine.connection
import threading, os, json, re
from queue import Queue
from web_scraping.file_tracker import FileLogger
import asyncio
from time import sleep
# Your settings and connection logic
from settings.settings import Settings
settings = Settings()

AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
AZURE_STORAGE_ACCOUNT_CRED = os.getenv("AZURE_STORAGE_ACCOUNT_CRED")
# Try disconnecting fi
# setup mongo connection
db_name = settings.MONGO_DB
db_conn = settings.MONGO_CONN_STR
print(f"db_name: {db_name}, db_conn: {db_conn}")
account_url = f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net"
fp = FileLogger(visited_log='visited.txt', rejected_log='rejected.txt', credentials=AZURE_STORAGE_ACCOUNT_CRED, account_url=account_url)
threads = []
doc_queue = Queue()

# this module simply moves files from the blob to mongo (easier access for processing and uploading to index)

def parse_json(json_data):
    metadata_dict = json_data.get("metadata", {})
    metadata = Metadata(
        source=metadata_dict.get("source", ""),
        last_updated=metadata_dict.get("last_updated", ""),
        title=metadata_dict.get("title", "")
    )

    document = WebPageDocument(
        page_content=json_data.get("page_content", []),
        metadata=metadata,
        type="Catalog"  # Assuming type is constant; adjust if it varies
    )

    return document

def save_document(doc):
    try:
        doc.save()
    except Exception as e:
        return str(e)
    
def extract_retry_after(error_message):
    try:
        # Search for the RetryAfterMs in the error message
        match = re.search(r"RetryAfterMs=(\d+)", error_message)
        if match:
            return int(match.group(1)) / 1000  # Convert ms to seconds
    except Exception as e:
        print(f"Failed to parse retry after time: {e}")
    return None  # Default to None if parsing fails


def run_move_file():
    while True and not doc_queue.empty():
        doc, filename = doc_queue.get()

        if doc is None and filename is None:
            break

        max_retries = 3  # Maximum number of retries
        for attempt in range(max_retries):
            try:
                # process completed threads:
                output = parse_json(doc)
                if len(output.page_content) < 2:
                    print(f"skipping {filename} due to empty content")
                    fp.rejected.add(filename)
                    break
                error_message = save_document(output)
                if error_message and 'Error=16500' in error_message:
                    retry_after = extract_retry_after(error_message)
                    if retry_after:
                        print(f"Rate limit exceeded:  retrying in {retry_after} seconds")
                        sleep(1+retry_after)
                        continue


                fp.visited.add(filename)
            

            except KeyboardInterrupt:  
                print("program interrupted, saving urls")  
                break
                #self.save_visited_urls()
            except Exception as e: 
                print(f"exception from qna {str(e)}")
                break
                #self.save_visited_urls( )
            
            #self.save_visited_urls()

def get_files(directory_path):
    if not os.path.exists(directory_path):
        print(f"Directory '{directory_path}' does not exist.")
        return None

    # Iterate over all files in the given directory
    for filename in os.listdir(directory_path):
        # Create full file path
        file_path = os.path.join(directory_path, filename)
        
        # Check if it is a file and not a directory
        if os.path.isfile(file_path):
            # Add file path to the queue
            with open(file_path, 'r') as file:
                try:
                    data = json.load(file)
                except Exception as e:
                    print(f"Error loading JSON file {file_path}: {e}")
                    continue

            page_content = data.get('page_content')
            if page_content:
                doc_queue.put((data, (data.get('metadata').get('source'))))

    return


# creates a thread pool to run qna processing (this is the main function to convert pages to short text)
async def chunked_files():
    max_threads = 15 # be careful of rate limiting and CPU usage
    get_files("/Users/marynelson/docs/itech_catalog")
            #start consumer thread production
    for _ in range(max_threads):
        thread = threading.Thread(target=run_move_file)
        threads.append(thread)
        thread.start()

    #await fp.get_docs_to_process("index-upload")
    # start producing docs in the queue
    #await fp.read_page_content_and_enqueue("index-upload")
    #doc_queue = fp.docs

    for thread in threads:
        thread.join()


try:    
    _mongo_conn = connect(db=db_name, host=db_conn)
    print(f"Connected to mongo: {_mongo_conn}")
    asyncio.run(chunked_files())
    

except Exception as e:
    print(f"Error connecting to mongo: {e}")



    