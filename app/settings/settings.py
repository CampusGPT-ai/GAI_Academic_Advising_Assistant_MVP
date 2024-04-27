from pydantic_settings import BaseSettings, SettingsConfigDict
import logging, os
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

logger.debug("logging environment variables --------------------------")

for name, value in os.environ.items():
     logger.debug("{0}: {1}".format(name, value))

class Settings(BaseSettings):

          
     model_config = SettingsConfigDict(case_sensitive=False, extra="allow")

     OPENAI_API_TYPE : str
     OPENAI_API_VERSION: str
     AZURE_OPENAI_ENDPOINT: str
     AZURE_OPENAI_API_KEY: str
     GPT4_DEPLOYMENT_NAME: str
     GPT4_MODEL_NAME: str
     GPT35_DEPLOYMENT_NAME: str
     GPT35_MODEL_NAME: str
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

     AZURE_CLIENT_ID: str
     AZURE_TENANT_ID: str
     AZURE_CLIENT_SECRET: str

     NON_SESSION_ID: str

     N4J_URI: str
     N4J_USERNAME: str
     N4J_PASSWORD: str

     UNIVERSITY_NAME: str
     
     SAML_METADATA_URL: str
     SAML_CERT: str
     
     BASE_URL: str
     CLIENT_BASE_URL: str
