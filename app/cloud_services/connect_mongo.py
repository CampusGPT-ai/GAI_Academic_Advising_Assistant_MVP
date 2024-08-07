from mongoengine import connect, disconnect
from settings.settings import Settings
import time, re

settings = Settings()
import mongoengine.connection

date_patterns = [
    r'\b\d{1,2}\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\b',  # 01 January
    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2}\b',  # January 1
    r'\b\d{2}/\d{2}\b',  # 01/18
    r'\b\d{2}-\d{2}\b'   # 01-18
]
combined_pattern = re.compile('|'.join(date_patterns))

class MongoConnection():
    # Try disconnecting fi
    # setup mongo connection
    def __init__(self):
        self.db_name = settings.MONGO_DB
        self.db_conn = settings.MONGO_CONN_STR
    # Function to disconnect all existing connections
    def disconnect_all():
        for alias in mongoengine.connection._connection_settings:
            disconnect(alias=alias)
            
    def connect(self):
        _mongo_conn = None
        try: 
            if not _mongo_conn:
                _mongo_conn = connect(db=self.db_name, host=self.db_conn)
                print(f"Connected to mongo: {_mongo_conn}")
                return _mongo_conn
        except Exception as e:
            print(f"Error connecting to mongo: {e}")

    def save_index_docs(self):
        import os, json
        from data.models import kbDocument

        documents = kbDocument.objects()

        # Fetch all documents from the collection
        path = "/Users/marynelson/Documents/mongo"

        if not os.path.exists(path):
            os.makedirs(path)

        for doc in documents:
            # Assuming each document has a unique identifier '_id'
            doc_dict = doc.to_mongo().to_dict()
            doc_dict.pop('_id')  # Remove the '_id' field
            file_path = os.path.join(path, f"{doc_dict['source'].replace('https://','').replace('.','_').replace(':','').replace('/','')}.json")
            
            # Write the document to a JSON file
            with open(file_path, 'w') as file:
                
                json.dump(doc_dict, file, default=str)  # Using default=str to handle any non-serializable data like datetime
    
    def delete_docs(self):
        from data.models import ConversationSimple
        ConversationSimple.objects().delete()

    def dedup_on_field(self):
        content_set = set()
        len = 0
        from data.models import WebPageDocument
        results = WebPageDocument.objects().all()
        for r in results:
            if r.page_content not in content_set:
                content_set.add(r.page_content)
                len = len + 1
            else:
                print(f"Duplicate found: {r.id}")
                r.delete()
        print(len)
    
    def flag_on_text(self):
        len = 0
        from data.models import WebPageDocument
        results = WebPageDocument.objects().all()
        for r in results:
            if bool(combined_pattern.search(r.page_content)):
                print(f"Flagging document: {r.id}")
                r.version="date_flagged"
                r.save()
                len = len + 1
        print(len)

    def count_docs(self):
        from data.models import WebPageDocumentNew  # Adjust the model name based on your actual models
        doc_count = WebPageDocumentNew.objects.count()
        print(doc_count)

    def delete_web_docs(self):
        from data.models import catalogDocument
        catalogDocument.objects().delete()
    
    def delete_docs_by_user(self, user):
        from data.models import ConversationSimple
        ConversationSimple.objects(user_id=user).delete()
        
    def delete_catalog_docs(self, retries=5, delay=1):
        from data.models import WebPageDocument
        results = WebPageDocument.objects(type="Catalog")
    
        for r in results:
            print(f"Deleting document: {r.id}")
            r.delete()

if __name__ == "__main__":
    mongo = MongoConnection()
    mongo.connect()
    mongo.count_docs()
    #mongo.delete_docs_by_user("A_iXG9LQjG86PTY1sgG-Sm9JO3IbMlliRkZok3BhT8I")

        