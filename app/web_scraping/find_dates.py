import re
from mongoengine import connect
from data.models import kbDocument, WebPageDocument
from dotenv import load_dotenv
from settings.settings import Settings
from queue import Queue
from web_scraping.qna import SyntheticQnA
import asyncio, os, json
import time
from pymongo.errors import OperationFailure

settings = Settings()

db_name = settings.MONGO_DB
db_conn = settings.MONGO_CONN_STR
_mongo_conn = connect(db=db_name, host=db_conn)
load_dotenv()

AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
AZURE_STORAGE_ACCOUNT_CRED = os.getenv("AZURE_STORAGE_ACCOUNT_CRED")
AZURE_STORAGE_CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER")

account_url = f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net"

mongo_docs = Queue()

loader = SyntheticQnA("visited.txt", "rejected.txt", credentials=AZURE_STORAGE_ACCOUNT_CRED, account_url=account_url)

# Define a regex pattern to match dates without a year
date_patterns = [
    r'\b\d{1,2}\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\b',  # 01 January
    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2}\b',  # January 1
    r'\b\d{2}/\d{2}\b',  # 01/18
    r'\b\d{2}-\d{2}\b'   # 01-18
]

# Combine all patterns into a single regex pattern
combined_pattern = re.compile('|'.join(date_patterns))
mongo_docs = Queue()
# Function to check if text contains a date without a year
def contains_date_without_year(text):
    return bool(combined_pattern.search(text))

# Simple retry logic function
def retry_with_backoff(func, max_retries=5, backoff_factor=2):
    for attempt in range(max_retries):
        try:
            return func()
        except OperationFailure as e:
            if e.code == 16500:
                retry_after_ms = e.details.get('RetryAfterMs', 1000)
                sleep_time = retry_after_ms / 1000
                print(f"Rate limit exceeded.  attempt: {attempt+1}. Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                raise
    raise Exception(f"Failed after {attempt} with {max_retries} retries")

# Function to query kbDocuments
def query_kb_documents():
    documents_with_dates = []
    for document in kbDocument.objects():
        if contains_date_without_year(document['text']):
            documents_with_dates.append({'source': document['source'], 'last_updated': document['updated']})
    return documents_with_dates

def save_document(doc):
    retry_with_backoff(doc.save)
# Function to query WebPageDocuments
def query_webpage_documents(source, last_updated):
    docs = WebPageDocument.objects(metadata__source=source, metadata__last_updated=last_updated)
    return docs

# Query all documents and check for dates without a year
documents_with_dates = retry_with_backoff(query_kb_documents)


# Output the sources of documents containing dates without a year
for source in documents_with_dates:
    docs = query_webpage_documents(source['source'], source['last_updated'])
    for attempt in range(5): 
        try:
            for doc in docs:
                doc.version = "v2"
                print("Saving document: ", doc.page_content)
                doc.save()
        except Exception as e:
            sleep_time = 2
            print(f"Rate limit exceeded.  attempt: {attempt+1}. Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)



print('starting chunk')
