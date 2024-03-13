from settings.settings import Settings
from mongoengine import connect, disconnect
from data.models import kbDocument
import time

settings = Settings()

db_name = settings.MONGO_DB
db_conn = settings.MONGO_CONN_STR

unique_sources = set()
documents_to_delete = []

def search_mongo():
    connect(db=db_name, host=db_conn)

    # Initialize an empty set to hold unique 'source' values
    for doc in kbDocument.objects():  # Query all documents
        if doc.text in unique_sources:
            documents_to_delete.append(doc.id)  # Add document ID to the list for deletion
        else:
            unique_sources.add(doc.text)

        # Process deletion in batches
        if len(documents_to_delete) >= YOUR_BATCH_SIZE:
            attempt_delete(documents_to_delete)
            documents_to_delete.clear()  # Clear the list after deletion

    # Attempt to delete any remaining documents in the batch
    if documents_to_delete:
        attempt_delete(documents_to_delete)
        documents_to_delete.clear()

    print(f"Unique sources: {len(unique_sources)}")

    disconnect()

def attempt_delete(doc_ids, max_attempts=5):
    attempts = 0
    while attempts < max_attempts:
        try:
            kbDocument.objects(id__in=doc_ids).delete()  # Batch delete operation
            break  # Exit the loop if delete is successful
        except Exception as e:  # Use a more generic exception if pymongo's OperationFailure isn't directly accessible
            error_code = getattr(e, 'code', None)
            if error_code == 16500:  # Check if the error is due to too many requests
                wait_time = (2 ** attempts) * 10  # Exponential backoff formula
                print(f"Rate limit exceeded, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                attempts += 1
            else:
                print(f"An error occurred: {e}")
                break  # Exit the loop if it's not a rate limit issue

YOUR_BATCH_SIZE = 25  # Adjust based on your RU limits and testing
search_mongo()
