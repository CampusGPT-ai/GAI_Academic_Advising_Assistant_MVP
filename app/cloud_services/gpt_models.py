from abc import ABC, abstractmethod
from langchain.chat_models import AzureChatOpenAI, ChatOpenAI
import logging, sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout)  # Ensures logs go to stdout
    ]
)

class AILLMModels(ABC):
    @abstractmethod
    def getModel(self):
        pass

    @abstractmethod
    def getEmbedding(self):
        pass

class AzureLLMModels:
    def __init__(self, 
                 deployment_name: str,
                 model_name: str,
                 embedding: str,
                 callbacks,
                 temperature: int = 0,
                 streaming: bool = True):
        self.model = AzureChatOpenAI(
                deployment_name=deployment_name,
                model_name=model_name,
                callbacks=callbacks,
                temperature=temperature,
                streaming=streaming
        )
        self.embedding = embedding

    def getModel(self):
        return self.model
    
    def getEmbedding(self):
        return self.embedding
    
class OpenAILLMModels:
    def __init__(self, 
                 model_name: str,
                 embedding: str,
                 callbacks,
                 temperature: int = 0,
                 streaming: bool = True):
        self.model = ChatOpenAI(
                model_name=model_name,
                callbacks=callbacks,
                temperature=temperature,
                streaming=streaming
        )
        self.embedding = embedding

    def getModel(self):
        return self.model
    
    def getEmbedding(self):
        return self.embedding
    
def get_llm_model(api_type: str, deployment_name: str, model_name: str, embedding: str) -> AILLMModels:
    logging.info(f"getting open ai models for {model_name}, {deployment_name}")
    if api_type == "azure":
        return AzureLLMModels(
                deployment_name=deployment_name,
                embedding=embedding,
                model_name=model_name,
                callbacks=[],
                temperature=0,
                streaming=True
        )
    else:
        return OpenAILLMModels(
                model_name=model_name,
                embedding=embedding,
                callbacks=[],
                temperature=0,
                streaming=True
        )
