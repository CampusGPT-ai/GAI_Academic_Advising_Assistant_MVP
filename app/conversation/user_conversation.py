# TODO: USER PROFILE
import openai, os, logging, sys, json, re

print(sys.path)

from typing import List
from settings.settings import Settings
from data.models import UserSession, RawChatMessage, Conversation, MessageContent, ChatMessage
from cloud_services.openai_response_objects import StreamingChatCompletion, Message
from conversation.prompt_templates.gpt_qa_prompt import get_gpt_system_prompt
from conversation.retrieve_docs import SearchRetriever
from user.get_user_info import UserInfo
from cloud_services.openai_response_objects import Message
from pathlib import Path
from urllib.parse import urldefrag
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


class UserConversation:

    def __init__(
        self,
        ai_model,
        search_client,
        settings: Settings,
        user_session: UserSession,
        conversation: Conversation
    ):
        self.ai_model = ai_model
        self.search_client = search_client
        self.settings = settings
        self.user_session : UserSession = user_session
        self.conversation: Conversation = conversation
        self.message_time: datetime = None

    @staticmethod
    def generate_gpt_prompt(user_info, rag, topics) -> Message:
        # Start with the system message
        system_instructions = get_gpt_system_prompt(user_info, rag, topics)
        return Message(role="system",content=system_instructions)

    @staticmethod
    def get_user_info() -> str :
        #removed demo profile here - might need to add back in future
        #TODO: pull in personalized data, remove temporary mock
        file_path = Path('data/test_user.json')
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return json.dumps(data)

    @staticmethod
    def parse_messages(message: Message) -> str:
        return message
    
    def get_conversation_history(self, prompt: List, query_text:str, conversation: Conversation):
        messages = []

        from conversation.retrieve_messages import get_message_history
        message_list = get_message_history(str(conversation.id), return_type='list')
        
        if message_list:
            try:
                for r in message_list:
                    messages.append(Message(role=r["role"], content=r["message"]))
                prompt.extend(messages)
            except Exception as e:
                logger.info(f"Unable to get message history with {str(e)}")

        user_message = Message(role="user", content=query_text)
        prompt.append(user_message)

        return prompt, user_message
    
    # TODO: remove - using conversation history instead
    def get_message_history(self, prompt: List, query_text: str):
        message_list = []

        try:
            raw_message_history: List[RawChatMessage] = RawChatMessage.objects(user_session_id=self.user_session)
        except Exception as e:
            raise Exception(f'Unable to get chat history from database with exception {str(e)}')
        
        if raw_message_history:
            try:
                for r in raw_message_history:
                    message_dict = json.loads(r.message)
                    message_list.append(Message(**message_dict))
                    logger.info(f"got message history item: {r.message}")
                prompt.extend(message_list)
            except Exception as e:
                logger.info(f"Unable to get message history with {str(e)}")

        user_message = Message(role="user", content=query_text)
        prompt.append(user_message)

        return prompt, user_message

    def save_conversation(self, messages, topics):
        if self.conversation != None:
            self.conversation.topic = topics
            self.conversation.messages.append(messages)
            try:
                self.conversation.save()
            except Exception as e:
                logger.error(f"unable to save conversation with {str(e)}")
                raise e
    
    def save_raw_chat(self, response_text: List[str], user_message: Message) -> None:
        content_string = "".join(response_text)
        message_list = []
        message_list.append(MessageContent(role=user_message.role, message=user_message.content, created_at=self.message_time))
        message_list.append(MessageContent(role='assistant', message=content_string))
        try:
            raw_chat = RawChatMessage(user_session_id=self.user_session,message=message_list)
            raw_chat.save()
            return raw_chat
        except Exception as e:
            logger.error("unable to save chat history for message.")
        return
    
    def get_augmented_chat(self, followups, citations, raw_chat):
        try:
            cm = ChatMessage(message=raw_chat,follow_up_questions=followups,citations=citations)
            return cm
        except Exception as e:
            logger.error("unable to save new chat message")

    @staticmethod
    def get_citations_from_text(cites: List, titles: dict, sources: dict) -> List[dict]:
        # Remove url fragments and deduplicate
        sources = [urldefrag(url).url for url in sources]
        sources = list(dict.fromkeys(sources))
        titles = list(dict.fromkeys(titles))

        for i in range(len(titles)):
            cites.append({"citation_text": titles[i], "citation_path": sources[i]})

        return cites
    
    def query_gpt(self, full_prompt: List[Message], user_message: Message, topics: List[str], followups: str, citations: List[dict]) -> bool:
        try:   
            # streaming access
            self.message_time = datetime.utcnow()
            azure_streaming_result = self.ai_model.stream(full_prompt) 
            finished = False
            response_text = []
            output: StreamingChatCompletion = None
            buffer = ''  # Buffer to hold incoming JSON chunks
            response_in_progress = False
            topic_index = 0
            response_index = 0
            while not finished:
                output = next(azure_streaming_result)
                if output and output.choices[0].delta.content:
                    output_text = output.choices[0].delta.content
                    output_text = output_text.replace(r'"',"").replace(r"```","").replace("json","")
                    output_text = output_text.replace("\n"," ").replace("{","").replace("}","")
                    if output_text == '' or output_text == ' ':
                        continue
                    buffer += output_text
                    response_index = buffer.find(r'response:')
                    topic_index = (buffer.find(r'topic: ')+len(r'topic: '))
                    if response_in_progress:
                        response_text.append(output_text)
                        yield {"event": "message", "data": json.dumps({'message': output_text})}
                        if (output_text.endswith(".\"") or output_text.endswith(".\"\n")) and response_in_progress:
                            response_in_progress = False
                    elif not response_in_progress and response_index != -1:
                        response_index_start = response_index + len(r'response: ')
                        response_in_progress = True
                        if buffer[response_index:] and buffer[response_index_start:] != '':
                            yield {"event": "message", "data": json.dumps({'message': buffer[response_index_start:] })}
                            response_text.append(buffer[response_index_start:])

                if output and output.choices[0].finish_reason == 'stop':

                    # try get topic from response:
                    new_topic = topics[0]
                    if topic_index > len(r'topic: '):
                        new_topic = buffer[topic_index:response_index-2]
                        new_topic = new_topic.replace(', ','')
                    # return conversation reference 
                    if self.conversation: 
                        c_dict = {
                            "topic": new_topic,
                            "id": str(self.conversation.id),
                            "start_time": self.conversation.start_time.isoformat() if self.conversation.start_time else None,
                            "end_time":self.conversation.end_time.isoformat() if self.conversation.end_time else None,
                        }

                    yield {"event": "conversation", "data": json.dumps({'message': c_dict})}
                    yield {"event": "topic", "data": json.dumps({'topic': new_topic})}
                    yield {"event": "followups","data": json.dumps({'followups': followups})}
                    for c in citations:
                        yield {"event": "citations", "data": json.dumps({'citations': c})}

                    # signal to close source in client
                    yield {"event": "stream-ended", "data": json.dumps({'stream-ended': 'true'})}
                    finished = True

        except Exception as e:
            yield {"event": "error", "data": json.dumps({'error': str(e)})}
            yield {"event": "stream-ended", "data": json.dumps({'stream-ended': 'true'})}
            logger.error(f"error on streaming response {str(e)}")
            raise e
        finally:
            try: 
                new_topic = buffer[topic_index:response_index-2]
                new_topic = new_topic.replace(', ','')
                logger.info(f'saving response with response text: {"".join(response_text)}')
                raw_chat = self.save_raw_chat(response_text, user_message)
                chat_message = self.get_augmented_chat(followups,citations,raw_chat)
                self.save_conversation(chat_message, new_topic)
                return finished
            except Exception as e: 
                yield {"event": "error", "data": json.dumps({'error': str(e)})}
                yield {"event": "stream-ended", "data": json.dumps({'stream-ended': 'true'})}
                logger.error(f'caught exception on saving chat message in finally {e}')
                raise e

    def send_message(self, query_text: str, conversation: Conversation) -> None:
        # Step 1: grab user info and existing conversation from source TODO: not implemented
        user_info = UserInfo(self.user_session).get_user_info()
               
        # Step 2: retrieve content from vector db (with default settings uses GPT 3.5)
        retriever = SearchRetriever.with_default_settings()
        content, followups = retriever.generate_content_and_questions(query_text, user_info)

        # step 3: create GPT prompt
        full_prompt = [self.generate_gpt_prompt(user_info, content['content'], content['keywords'])]

        # step 4: add message history
        #full_prompt, user_message = self.get_message_history(full_prompt, query_text)
        full_prompt, user_message = self.get_conversation_history(full_prompt, query_text, conversation)

        # step 5: get citations
        citations = []
        if 'title' in content and 'source' in content:
            if content['title'] == None or content['title'] == '':
                content['title'] = content['source']
            citations = self.get_citations_from_text(citations, content['title'], content['source'])

        # step 5: query generator
        try:   
            yield from self.query_gpt(full_prompt, user_message,  content['keywords'], followups, citations)
        except openai.APIConnectionError as e:
            logger.info(f"Caught APIConnectionError: {e}")
            raise e
        except Exception as e:
            logger.info(f"Caught exception: {e}")
            raise e

    @classmethod           
    def with_default_settings(cls, user_session: UserSession, conversation: Conversation, model_num='GPT35'):
        from cloud_services.llm_services import get_llm_client
        from cloud_services.azure_cog_service import AzureSearchService
        # Assume these are your default settings or loaded from a config file/environment

        default_settings = Settings()
        
        if model_num=='GPT35':
            selected_model = default_settings.GPT35_MODEL_NAME
            selected_deployment = default_settings.GPT35_DEPLOYMENT_NAME
        else:
            selected_model = default_settings.GPT4_MODEL_NAME,
            selected_deployment = default_settings.GPT4_DEPLOYMENT_NAME

        
        azure_llm = get_llm_client(api_type='azure',
                                api_version=default_settings.OPENAI_API_VERSION,
                                endpoint=default_settings.AZURE_OPENAI_ENDPOINT,
                                model=selected_model,
                                deployment=selected_deployment,
                                embedding_deployment=default_settings.EMBEDDING)

        # Create an instance of the class with these default settings
        return cls(
            ai_model=azure_llm,
            search_client=AzureSearchService(default_settings.SEARCH_ENDPOINT,
                                                default_settings.SEARCH_INDEX_NAME,
                                                azure_llm,
                                                default_settings.SEARCH_API_KEY),
            settings=default_settings,
            user_session=user_session,
            conversation=conversation
        )


if __name__=="__main__":

    from mongoengine import connect

    db_name = os.getenv("MONGO_DB")
    db_conn = os.getenv("MONGO_CONN_STR")
    _mongo_conn = connect(db=db_name, host=db_conn)


    from pathlib import Path
    logger.debug(f"Current Working Directory: {os.getcwd()}")
    relative_path = Path('./app/data/mock_user_session.json')


    with relative_path.open(mode='r') as file:
        mock_user_session : UserSession = UserSession(**json.load(file))
    
    mock_conversation = Conversation(id="65cd0b42372b404efb9805f6")

    convo = UserConversation.with_default_settings(mock_user_session, mock_conversation, model_num='GPT4')
    
    result = convo.send_message("what classes do I need to graduate?", mock_conversation)
    while True:
        logger.info(next(result))

