from mongoengine import connect, disconnect
from settings.settings import Settings

settings = Settings()
import mongoengine.connection


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

    def save_doc(self):
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

if __name__ == "__main__":
    mongo = MongoConnection()
    mongo.connect()
    mongo.save_doc()
    mongo.disconnect_all()
    print("Disconnected from mongo")

        