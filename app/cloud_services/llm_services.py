from abc import ABC, abstractmethod
from openai import AzureOpenAI, OpenAI
import openai, json
from azure.identity import DefaultAzureCredential
import logging, sys, os
import cloud_services.openai_response_objects as openai_response_objects
from cloud_services.openai_response_objects import Message, Embedding, ChatCompletion, StreamingChatCompletion
import tiktoken, re
from typing import List 
from langchain_openai import AzureOpenAIEmbeddings
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

 
logger = logging.getLogger(__name__)

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

class OpenAIClients(AILLMClients):
    def __init__(self, model: str, api_key: str):
        os.environ["OPENAI_API_KEY"] = api_key

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def chat(self, messages: List[Message], json_mode: bool = False) -> ChatCompletion:
        # Convert messages to the format expected by OpenAI
        prompts = [msg.model_dump_json() for msg in messages]
        
        try:
            if json_mode:
                result = self.client.chat.completions.create(
                    model=self.model,
                    response_format={ "type": "json_object" },
                    messages=prompts
                )
            else:
                result = self.client.chat.completions.create(
                    model=self.model,
                    messages=prompts,
                    max_tokens=250
                )
            return openai_response_objects.parse_completion_object(False,result)
        except Exception as e:
            raise e
        
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
                api_key=os.getenv("AZURE_OPENAI_KEY"),  
                api_version=api_version
)
        self.model = model
        self.deployment = deployment
        self.embedding_deployment = embedding_deployment

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
        
    def validate_json(self, string_response, string_list):
        output = None
        try:
            dict = json.loads(string_response)
            if not dict or dict == {}:
                raise Exception(f"input dictionary is not valid JSON: {dict} ")
        except Exception as e:
            raise e
        for l in string_list:
            logger.info(f"checking for {l}")
            try: 
                output = dict.get(l)
                if not output:
                    raise Exception(f"key {l} not found in response {dict}")
            except Exception as e:
                logger.error(f'error parsing json from LLM response: {str(e)}')
                raise e
        return dict
    
    @staticmethod
    def _format_json(gpt_response):
        response = gpt_response.choices[0].message.content
        formatted_response = response.replace("\n", "").replace(r"```", "").replace("json", "").replace("{ ","{")
        formatted_response = formatted_response.replace("</p><br>", "</p>").replace("<br><ul>", "<ul>")
        return formatted_response


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
                result = self.client.embeddings.create(input=text, model=self.embedding_deployment)
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
            logger.info(f"text greater than max tokens detected {len(cleaned_inputs)-len(filtered_inputs)} items filtered out of embedding")
        result = []    
        try:
            result = self.client.embeddings.create(input=filtered_inputs, model=self.embedding_deployment)
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
    logger.info(f"getting open ai clients for {api_type}, {model}")
    
    if api_type == "azure":
        return AzureLLMClients(
                api_version=api_version,
                azure_endpoint=endpoint,
                model=model,
                deployment=deployment,
                embedding_deployment=embedding_deployment
        )
    
    if api_type == "openai":
        return OpenAIClients(
                model=model,
                api_key=api_key
        )


if __name__ == "__main__":
    import dotenv, os
    dotenv.load_dotenv()

    from settings.settings import Settings
    settings = Settings()

    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    OPENAI_API_KEY = settings.OPENAI_API_KEY
    OPENAI_DIRECT_MODEL = settings.OPENAI_DIRECT_MODEL
    OPENAI_VERSION = os.getenv("OPENAI_API_VERSION")
    OPENAI_ENDPOINT= os.getenv("AZURE_OPENAI_ENDPOINT")
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

    openai_client : OpenAIClients = get_llm_client(api_type='openai',
                                                    model=OPENAI_DIRECT_MODEL,
                                                    api_key=OPENAI_API_KEY)
    
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
    openai_result = openai_client.chat(messages=default_messages)
    # langchain_embedding = langchain_client.embed("some text to embed")
    # azure_embedding = azure_llm_client.embed("some text to embed")
    
    # streaming access
    #finished = False
    #while not finished:
    #    output : StreamingChatCompletion = next(azure_streaming_result)
    #    if output:
    #        output_text = output.choices[0].delta.content
    #        if output_text != None:
    #            logger.info(output_text)
    #        if output.choices[0].finish_reason == 'stop':
    #            finished = True
        

