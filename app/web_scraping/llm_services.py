from abc import ABC, abstractmethod
from openai import AzureOpenAI, OpenAI
import openai
from azure.identity import DefaultAzureCredential
import logging, sys, os
import openai_response_objects as openai_response_objects
from openai_response_objects import Message, Embedding, ChatCompletion, StreamingChatCompletion
import tiktoken, re
from typing import List 
from langchain_openai import AzureOpenAIEmbeddings
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

credential = DefaultAzureCredential()
TOKEN = credential.get_token("https://cognitiveservices.azure.com/.default").token
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_type = 'azure_ad'
        
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout)  # Ensures logs go to stdout
    ]
)

def normalize_text(s, sep_token = " \n "):
    s = re.sub(r'\s+',  ' ', s).strip()
    s = re.sub(r". ,","",s)
    # remove all instances of multiple spaces
    s = s.replace("..",".")
    s = s.replace(". .",".")
    s = s.replace("\n", "")
    s = s.strip()
    
    return s

"""
Tokenizes the given text using the 'cl100k_base' tokenizer.

Args:
    text (str): The input text to be tokenized.

Returns:
    List[int]: The encoded tokens representing the input text.
    """
def get_tokens(text):

    tokenizer = tiktoken.get_encoding("cl100k_base")
    encoding = tokenizer.encode(text)
    return len(encoding)



def convert_to_langchain(messages: List[Message]):
    message_list =  [model.model_dump() for model in  messages]
    m = []
    for message in message_list:
        if message["role"] == 'system':
            m.append(SystemMessage(content=message["content"]))
        elif message["role"] == 'user':
            m.append(HumanMessage(content=message["content"]))
    return m


"""
Abstract base class for AILLM clients.
"""                  
class AILLMClients(ABC):


    @abstractmethod
    def chat(self):
        pass

    def embed(self):
        pass
    
    def embed_to_array(self):
        pass
    
"""
A class representing LangChain Language Model clients.

Args:
    deployment (str): The deployment environment.
    version (str): The version of the language model.
    endpoint (str): The endpoint URL.

Attributes:
    client (AzureChatOpenAI): The Azure Chat OpenAI client.
    embeddings (AzureOpenAIEmbeddings): The Azure OpenAI Embeddings client.

Methods:
    chat(messages: List[Message]) -> Any:
        Sends a chat request to the language model and returns the response.

    embed(text: str) -> List[float]:
        Embeds the given text using the embedding model.

    """    
class LangChainLLMClients(AILLMClients):

    def __init__(self,
                 deployment: str,
                 version: str,
                 endpoint: str):

        self.client = AzureChatOpenAI(openai_api_version=version,
                                      azure_deployment=deployment,
                                      azure_endpoint=endpoint)
        self.embeddings = AzureOpenAIEmbeddings(azure_deployment='embedding', 
                                                openai_api_version=version,
                                                azure_endpoint=endpoint)
        
    def chat(self, messages):
        result = self.client.invoke(messages)
        return openai_response_objects.parse_completion_object(False, result)
    
    def embed(self, text) -> Embedding:
        result = self.embeddings.embed_query(text)
        return openai_response_objects.parse_embedding({"embedding": result})
    
    def embed_to_array(self, text):
        embedding = self.embed(text)
        return embedding.embedding
    
class AzureLLMClients(AILLMClients):
    """
    A class representing Azure Language Model (LLM) clients.

    Args:
        azure_endpoint (str): The Azure endpoint URL.
        model (str): The name of the LLM model.
        embedding_deployment (str): The deployment name for text embedding.
        deployment (str): The deployment name for chat.
        api_version (str, optional): The API version. Defaults to "2023-12-01-preview".

    Attributes:
        chat_client (AzureOpenAI): The Azure OpenAI client for chat.
        embedding_client (AzureOpenAI): The Azure OpenAI client for text embedding.
        model (str): The name of the LLM model.

    Methods:
        chat: Sends a list of messages to the chat model and returns the response.
        embed: Embeds a text using the text embedding model.
        embed_many: Embeds multiple texts using the text embedding model.
        embed_to_array: Embeds a text and returns the embedding as an array.
    """
    def __init__(self, 
                 azure_endpoint: str,
                 model: str,
                 embedding_deployment: str,
                 deployment: str,
                 api_version: str = "2023-05-15",
                ):
        self.client  = AzureOpenAI(
                azure_endpoint = azure_endpoint, 
                api_key=os.getenv("OPENAI_API_KEY"),  
                api_version=api_version
)
        self.model = model
        self.deployment = deployment

    def stream(self, messages: List[Message]):
        message_list =  [model.model_dump() for model in  messages]

        try:
            result = self.client.chat.completions.create(
                model = self.deployment,
                messages = message_list,
                stream=True
            )

            for chunk in result:
                yield openai_response_objects.parse_completion_object(True,chunk)
        except Exception as e:
            raise e

    def chat(self, messages: List[Message], json_mode: bool = False) -> ChatCompletion:
        """
        Sends a list of messages to the chat model and returns the response.

        Args:
            messages (List[Message]): The list of messages to send.
            json_mode (bool, optional): Whether to return the response in JSON format. Defaults to False.

        Returns:
            The response from the chat model.
        """
        message_list =  [model.model_dump() for model in  messages]
        try:
            if json_mode and self.model in ('gpt-4-1106-preview','gpt-35-turbo-1106'):
                result = self.client.chat.completions.create(
                    model = self.deployment,
                    seed = 42,
                    response_format={ "type": "json_object" },
                    messages = message_list
                    )
            else:
                result = self.client.chat.completions.create(
                    model = self.deployment,
                    messages = message_list
                    )
            return openai_response_objects.parse_completion_object(False,result)
        except Exception as e:
            raise e
    
    def embed(self, text) -> Embedding:
        """
        Embeds a text using the text embedding model.

        Args:
            text (str): The text to embed.

        Returns:
            The embedding of the text.
        """
        clean_text = normalize_text(text)
        tokens = get_tokens(clean_text)
        if tokens < 8192:
            try:
                result = self.client.embeddings.create(input=text, model="embeddings")
            except Exception as e:
                raise e
        else: 
            raise Exception("length exceeds azure limitation of 8192 tokens")
        
        return openai_response_objects.parse_embedding(result.data[0])
    
    def embed_many(self, inputs: List[str]) -> List[Embedding]:
        """
        Embeds multiple texts using the text embedding model.

        Args:
            inputs (List[str]): The list of texts to embed.

        Returns:
            a list of pydantic Embeddings.  Access floats with Embedding.embedding
        """
        cleaned_inputs = [(text, get_tokens(normalize_text(text))) for text in inputs]
        filtered_inputs = [text for text, token_count in cleaned_inputs if token_count <= 8192]
        if len(cleaned_inputs)-len(filtered_inputs) > 0:
            logging.info(f"text greater than max tokens detected {len(cleaned_inputs)-len(filtered_inputs)} items filtered out of embedding")
        result = []    
        try:
            result = self.client.embeddings.create(input=filtered_inputs, model="text-embedding-ada-002")
        except Exception as e:
            raise e
        
        return openai_response_objects.parse_embedding(result.data)
    
    def embed_to_array(self, text):
        """
        Embeds a text and returns the embedding as an array.

        Args:
            text (str): The text to embed.

        Returns:
            The embedding of the text as an array.
        """
        embedding = self.embed(text)
        return embedding.embedding



class OpenAILLMClients(AILLMClients):
    """
A class representing OpenAI language model clients.

Args:
    model (str): The name of the language model.
    embedding_model (str): The name of the embedding model.
    api_key (str): The API key for accessing OpenAI services.

Attributes:
    client: The OpenAI client object.
    model (str): The name of the language model.
    embeddings (str): The name of the embedding model.
"""
    
    def __init__(self, model, api_key, embedding_model):
        self.client = OpenAI()
        self.api_key = api_key
        self.model = model
        self.embeddings = embedding_model
        
    # Creates a model response for the given chat conversation.    
    def chat(self, is_streaming: bool,  messages: List[Message]) -> ChatCompletion:
        message_list =  [model.model_dump() for model in  messages]
        try:
            result = self.client.chat.completions.create(
                model = self.model,
                messages = message_list
            )
        except Exception as e:
            raise e
        return openai_response_objects.parse_completion_object(is_streaming,result)

    def embed(self, text) -> openai_response_objects.Embedding:
        clean_text = normalize_text(text)
        try:
            result = self.client.embeddings.create(
                model=self.embeddings,
                input=clean_text,
                encoding_format='float'
            )
            return (
                openai_response_objects.parse_embedding(result)
                    )
        except Exception as e: 
            raise e
        
    def embed_to_array(self, text):
        embedding = self.embed(text)
        return embedding.embedding
    
  
def get_llm_client(api_type: str,
                   model: str = None,
                   api_key=None,
                   embedding_model=None,
                   embedding_deployment=None,
                   api_version=None,
                   endpoint=None,
                   deployment=None) -> AILLMClients:
    """
Get the appropriate LLM client based on the specified API type.

Args:
    api_type (str): The type of LLM API to use (e.g., "azure", "langchain", "openai").
    model (str, optional): The LLM model to use. required for Azure and Open AI.  
    api_key (str, optional): The API key to use. Required for Open AI only
    embedding_model (str, optional): The embedding model to use. required for open AI only
    endpoint (str, optional): The API endpoint to use. Required for langchain and azure only
    deployment (str, optional): The deployment to use. required for langchain and azure only
    embedding_deployment (str, optional): the deployment name in azure for the embedding model. 
       required for azure only.

Returns:
    AILLMClients: An instance of the appropriate LLM client based on the specified API type.
"""  
    logging.info(f"getting open ai clients for {api_type}, {model}")
    
    if api_type == "azure":
        return AzureLLMClients(
                api_version=api_version,
                azure_endpoint=endpoint,
                model=model,
                deployment=deployment,
                embedding_deployment=embedding_deployment
        )

    elif api_type == "langchain": 
        return LangChainLLMClients(deployment=deployment,
                                   version=api_version,
                                   endpoint=endpoint)

    else: 
        return OpenAILLMClients(
            model=model,
            api_key=api_key,
            embedding_model=embedding_model
        )


if __name__ == "__main__":
    import dotenv, os
    dotenv.load_dotenv()

    AZURE_OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_VERSION = os.getenv("OPENAI_API_VERSION")
    OPENAI_ENDPOINT= os.getenv("AZURE_ENDPOINT")
    OPENAI_DEPLOYMENT = os.getenv("DEPLOYMENT_NAME")
    OPENAI_MODEL = os.getenv("MODEL_NAME")
    EMBEDDING_DEPLOYMENT = os.getenv("EMBEDDING")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
    SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
    SEARCH_API_KEY= os.getenv("SEARCH_API_KEY")
    SEARCH_INDEX_NAME=os.getenv("SEARCH_INDEX_NAME")


    azure_llm_client : AzureLLMClients = get_llm_client(api_type='azure',
                                                        api_version=OPENAI_VERSION,
                                                        endpoint=OPENAI_ENDPOINT,
                                                        model=OPENAI_MODEL,
                                                        deployment=OPENAI_DEPLOYMENT,
                                                        embedding_deployment=EMBEDDING_DEPLOYMENT)

    
    langchain_client: LangChainLLMClients = get_llm_client(api_type='langchain',
                                                               deployment=OPENAI_DEPLOYMENT,
                                                               api_version=OPENAI_VERSION,
                                                               endpoint=OPENAI_ENDPOINT)
    
    openai_client: OpenAILLMClients = get_llm_client(api_type='openai', 
                                                     model="gpt-4-1106-preview",
                                                     api_key=TOKEN,
                                                     embedding_model=EMBEDDING_MODEL)
    
    QUERY_TEXT = "what dining services are available on UCF campus"
    SYSTEM_TEXT = "You are an academic advising assistant.  Answer your students questions"
    
    default_messages = [
        Message(role='system', content=SYSTEM_TEXT),
        Message(role='user',content=QUERY_TEXT)
    ]
    
    langchain_messages = convert_to_langchain(default_messages)
    
    # langchain_result = langchain_client.chat(langchain_messages)
    # azure_result = azure_llm_client.chat(default_messages)
    azure_streaming_result = azure_llm_client.stream(default_messages)
    # openai_result = openai_client.chat(is_streaming=False, messages=default_messages)
    # langchain_embedding = langchain_client.embed("some text to embed")
    # azure_embedding = azure_llm_client.embed("some text to embed")
    
    # streaming access
    finished = False
    while not finished:
        output : StreamingChatCompletion = next(azure_streaming_result)
        if output:
            output_text = output.choices[0].delta.content
            if output_text != None:
                print(output_text)
            if output.choices[0].finish_reason == 'stop':
                finished = True
        

