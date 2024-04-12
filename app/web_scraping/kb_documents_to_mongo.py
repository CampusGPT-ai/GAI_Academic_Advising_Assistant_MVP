from mongoengine import connect, disconnect
from data.models import kbDocument
import mongoengine.connection
import threading, os
from web_scraping.file_tracker import FileLogger
import asyncio
# Function to disconnect all existing connections
def disconnect_all():
    for alias in mongoengine.connection._connection_settings:
        disconnect(alias=alias)

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

# this module simply moves files from the blob to mongo (easier access for processing and uploading to index)

def parse_json(json_data):
    output = []

    for qna_item in json_data.get("qna", []):
        dict_item = kbDocument(
            source = json_data.get("metadata", {}).get("source", ""),
            updated = json_data.get("metadata", {}).get("last_updated", ""),
            text = qna_item
        )
        output.append(dict_item)

    return output


def run_move_file():
    while True:
        doc, filename = fp.docs.get()

        if doc is None and filename is None:
            break

        max_retries = 3  # Maximum number of retries
        retry_delay = 10  # Delay in seconds
        for attempt in range(max_retries):
            try:
                # process completed threads:
                output = parse_json(doc)
                for o in output:
                    o.save()

                fp.visited.add(filename)

            except KeyboardInterrupt:  
                print("program interrupted, saving urls")  
                #self.save_visited_urls()
            except Exception as e: 
                print(f"exception from qna {str(e)}")
                #self.save_visited_urls( )
            
            #self.save_visited_urls()

# creates a thread pool to run qna processing (this is the main function to convert pages to short text)
async def chunked_files():
    max_threads = 15 # be careful of rate limiting and CPU usage
            #start consumer thread production
    for _ in range(max_threads):
        thread = threading.Thread(target=run_move_file)
        thread.start()
        threads.append(thread)

    await fp.get_docs_to_process("index-short-text")
    # start producing docs in the queue
    await fp.read_page_content_and_enqueue("index-short-text")

    for _ in threads: 
        fp.docs.put((None,None))

    for thread in threads:
        thread.join()


try:    
    _mongo_conn = connect(db=db_name, host=db_conn)
    print(f"Connected to mongo: {_mongo_conn}")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(chunked_files())
    loop.close
    

except Exception as e:
    print(f"Error connecting to mongo: {e}")
finally:
    disconnect_all()


    