from mongoengine import connect, disconnect

import mongoengine.connection


# Function to disconnect all existing connections
def disconnect_all():
    for alias in mongoengine.connection._connection_settings:
        disconnect(alias=alias)

# Your settings and connection logic
from settings.settings import Settings
settings = Settings()

# Try disconnecting fi
# setup mongo connection
db_name = settings.MONGO_DB
db_conn = settings.MONGO_CONN_STR
print(f"db_name: {db_name}, db_conn: {db_conn}")
try:    
    _mongo_conn = connect(db=db_name, host=db_conn)
    print(f"Connected to mongo: {_mongo_conn}")
    disconnect_all()
except Exception as e:
    print(f"Error connecting to mongo: {e}")


    