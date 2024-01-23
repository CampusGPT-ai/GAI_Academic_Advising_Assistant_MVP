from pydantic_settings import BaseSettings, SettingsConfigDict
import logging, os
from dotenv import load_dotenv
load_dotenv()
logging.info("logging environment variables --------------------------")
for name, value in os.environ.items():
     logging.info("{0}: {1}".format(name, value))
class Settings(BaseSettings):

          
     model_config = SettingsConfigDict(case_sensitive=False, extra="allow")
     
     APPSETTING_OPENAI_API_KEY: str
     APPSETTING_OPENAI_API_TYPE : str
     APPSETTING_OPENAI_API_BASE: str
     APPSETTING_OPENAI_API_VERSION: str
     APPSETTING_DEPLOYMENT_NAME: str
     APPSETTING_MODEL_NAME: str
     APPSETTING_EMBEDDING: str
     APPSETTING_MONGO_DB: str
     APPSETTING_MONGO_CONN_STR: str
     APPSETTING_RAW_MESSAGE_COLLECTION: str
     APPSETTING_HISTORY_WINDOW_SIZE: int

     
     APPSETTING_SEARCH_ENDPOINT: str
     APPSETTING_SEARCH_API_KEY: str
     APPSETTING_SEARCH_INDEX_NAME: str
     APPSETTING_KB_FIELDS_SOURCEPAGE: str
     APPSETTING_KB_FIELDS_CONTENT: str
     
     APPSETTING_AZURE_STORAGE_ACCOUNT: str
     APPSETTING_AZURE_STORAGE_ACCOUNT_CRED: str
     APPSETTING_AZURE_STORAGE_CONTAINER: str
     
