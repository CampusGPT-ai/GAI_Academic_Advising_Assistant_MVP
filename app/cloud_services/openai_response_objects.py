from pydantic import BaseModel, validator
from typing import Optional, List, Union
from datetime import datetime

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class Message(BaseModel):
    role: str
    content: str
    
class Function(BaseModel):
    name: str
    arguments: str

class ToolCall(BaseModel):
    index: int
    id: str
    type: str
    function: Optional[Function]
        
class Delta(BaseModel):
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    
class BaseEmbedding(BaseModel):
    embedding: List[float]

class Embedding(BaseEmbedding):
    object: Optional[str] = None
    embedding: List[float]
    index: Optional[int] = None
    text: Optional[str] = None
    summary: Optional[str] = None
    title: Optional[str] = None
    n_tokens: Optional[int] = None
    
class BaseMessage(BaseModel):
    content: str

class ChatCompletionMessage(BaseMessage):
    role: str
    function_call: Optional[str]

class AIMessage(BaseMessage):
    pass

class Choice(BaseModel):
    finish_reason: Optional[str] = None
    index: int
    logprobs: Optional[str]
    message: Union[ChatCompletionMessage, AIMessage]

class ChoiceDelta(BaseModel):
    content: Optional[str] = None
    function_call: Optional[str] = None
    role: Optional[str] = None
    tool_calls: Optional[str] = None

class StreamingDelta(BaseModel):
    delta: ChoiceDelta
    finish_reason: Optional[str] = None
    index: int
    logprobs: Optional[str]

class StreamingChatCompletion(BaseModel):
    id: str
    choices: List[StreamingDelta]
    created: datetime
    model: str
    object: str
    system_fingerprint: Optional[str] = None

    @validator('created', pre=True)
    def convert_timestamp_to_datetime(cls, value):
        if isinstance(value, int):
            return datetime.utcfromtimestamp(value)
        elif isinstance(value, datetime):
            return value
        raise ValueError("Invalid type for 'created', must be int or datetime")
       

class ChatCompletion(BaseModel):
    id: str
    choices: List[Choice]
    created: datetime
    model: str
    object: str
    system_fingerprint: Optional[str] = None
    usage: dict

    @validator('created', pre=True)
    def convert_timestamp_to_datetime(cls, value):
        if isinstance(value, int):
            return datetime.utcfromtimestamp(value)
        elif isinstance(value, datetime):
            return value
        raise ValueError("Invalid type for 'created', must be int or datetime")
    
class ChatCompletionChunk(BaseModel):
    id: str
    choices: List[Choice]
    created: datetime
    model: str
    system_fingerprint: str
    object: str
    
    @validator('created', pre=True)
    def convert_timestamp_to_datetime(cls, value):
        return datetime.utcfromtimestamp(value)
    
def to_dict(obj):

    if isinstance(obj, list):
        return [to_dict(item) for item in obj]
    elif hasattr(obj, "__dict__"):
        return {key: to_dict(value) for key, value in obj.__dict__.items()}
    else:
        return obj

# Function to parse the JSON string into a Pydantic object
def parse_completion_object(is_streaming: bool, json_string: object) -> ChatCompletion:
    obj_dict = to_dict(json_string)
    try:
        if is_streaming:
            if obj_dict["id"] == '':
                #incomplete stream
                return None
            else:
                return StreamingChatCompletion(**obj_dict)
        else:
            return ChatCompletion(**obj_dict)
    except Exception as e:
        raise e
    
def parse_completion_string(is_streaming: bool, json_string: str) -> ChatCompletion:
    if is_streaming:
        return ChatCompletion.model_validate_json(json_string)
    else:
        return ChatCompletion.model_validate_json(json_string)

def parse_embedding(json_string: str) -> Embedding:
    obj_dict = to_dict(json_string)
    return Embedding(**obj_dict)

