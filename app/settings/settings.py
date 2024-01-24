from pydantic_settings import BaseSettings, SettingsConfigDict
import logging, os
from dotenv import load_dotenv
load_dotenv()
logging.info("logging environment variables --------------------------")
for name, value in os.environ.items():
     logging.info("{0}: {1}".format(name, value))
class Settings(BaseSettings):

          
     model_config = SettingsConfigDict(case_sensitive=False, extra="allow")

     OPENAI_API_TYPE : str
     OPENAI_API_VERSION: str
     AZURE_OPENAI_ENDPOINT: str
     AZURE_OPENAI_API_KEY: str
     DEPLOYMENT_NAME: str
     MODEL_NAME: str
     EMBEDDING: str
     MONGO_DB: str
     MONGO_CONN_STR: str
     RAW_MESSAGE_COLLECTION: str
     HISTORY_WINDOW_SIZE: int

     
     SEARCH_ENDPOINT: str
     SEARCH_API_KEY: str
     SEARCH_INDEX_NAME: str
     KB_FIELDS_SOURCEPAGE: str
     KB_FIELDS_CONTENT: str
     
     AZURE_STORAGE_ACCOUNT: str
     AZURE_STORAGE_ACCOUNT_CRED: str
     AZURE_STORAGE_CONTAINER: str
     
     APP_NAME: str
     