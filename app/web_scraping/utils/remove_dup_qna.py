from mongoengine import connect
from settings.settings import Settings
settings = Settings()
from data.models import kbDocument, WebPageDocument, Metadata
# Connect to the default database
db_name = settings.MONGO_DB
db_conn = settings.MONGO_CONN_STR
_mongo_conn = connect(db=db_name, host=db_conn)

def remove_duplicate_documents():
    texts_seen = set()
    duplicates = []

    # Fetch all documents in the collection
    for doc in kbDocument.objects:
        if doc.text in texts_seen:
            # If the text is already seen, mark this document for deletion
            duplicates.append(doc)
        else:
            # If it's a new text, remember it
            texts_seen.add(doc.text)

    # Remove all duplicates identified
    for duplicate in duplicates:
        duplicate.delete()

    print(f"Removed {len(duplicates)} duplicate documents.")

def remove_doc_by_content():
    # Fetch all documents in the collection
    for doc in WebPageDocument.objects:
        if len(doc.page_content) <2:
            doc.delete()
            print(f"Removed document with content: {doc.page_content}")
    


def get_unique_source_counts():
    # Perform an aggregation to group documents by the 'source' field,
    # count the number of documents for each source, and sort the results
    pipeline = [
        {
            '$group': {
                '_id': '$source',  # Group by the 'source' field
                'count': {'$sum': 1}  # Count the number of documents in each group
            }
        },
        {
            '$sort': {'count': -1}  # Sort the groups by count in descending order
        }
    ]
    results = list(kbDocument.objects.aggregate(*pipeline))
    
    # Convert the results to a more readable format
    formatted_results = [{'source': item['_id'], 'count': item['count']} for item in results]
    return formatted_results

def print_texts_by_source(source_name):
    # Query the collection for documents with the given source
    documents = kbDocument.objects(source=source_name)
    
    # Check if any documents were found
    if documents:
        print(f"Texts of documents from source '{source_name}':")
        for doc in documents:
            print(doc.text)
    else:
        print(f"No documents found for source '{source_name}'.")

if __name__ == '__main__':
    remove_doc_by_content()
