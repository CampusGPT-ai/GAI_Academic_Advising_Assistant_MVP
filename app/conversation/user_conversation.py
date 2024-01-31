# TODO: USER PROFILE
import openai, os
import asyncio

from operator import itemgetter
from typing import AsyncIterable
from cloud_services.gpt_models import AILLMModels
from cloud_services.vector_search import VectorSearchService
from langchain.schema import SystemMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories.mongodb import MongoDBChatMessageHistory
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.schema import ChatGeneration
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from settings.settings import Settings
from conversation.streaming_parser import StreamingParser
from util.logger_format import CustomFormatter
import logging, sys
from conversation.prompt_templates.gpt_qa_prompt import get_gpt_system_prompt
from conversation.prompt_templates.search_string_prompt import get_keyword_prompt

ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.handlers.clear()  
logger.addHandler(ch)  


def nonewlines(s: str) -> str:
    return s.replace('\n', ' ').replace('\r', ' ')


def get_optimized_keyword_prompt(user_question, user_info) -> ChatPromptTemplate:
    system_instructions = get_keyword_prompt(user_question, user_info)
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=(system_instructions)),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("User Profile: {user_info}\n\n User Question: {user_query}\n\n")
    ])
    return prompt


def generate_gpt_prompt(user_info) -> ChatPromptTemplate:
    # Start with the system message

    system_instructions = get_gpt_system_prompt(user_info)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=(system_instructions)),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template(
            "{user_question}\n\nSources:\n{sources}") 
    ])
    logger.info(f"generated prompt template: {prompt}")
    return prompt

def get_user_info():
    
    #removed demo profile here - might need to add back in future
    #TODO: pull in personalized data 
    return {"none provided"}

def generate_follow_up_prompt() -> ChatPromptTemplate:
    response_schemas = [
        ResponseSchema(name="followups", type="string", description="the three most likely follow up questions of interest as a list element"),
        ResponseSchema(name="topic", type="string", description="what is the main subject of question the user asked? use no more than 3 words.")
    ]
        
    output_parser = StructuredOutputParser(response_schemas=response_schemas)
    format_instructions = output_parser.get_format_instructions()

    follow_up_template =  """
Based on the history of the conversation and the users question, generate 2 things:
- three very brief follow-up questions that the user would likely ask next given the users previous question. Only generate questions and do not generate any text before 
or after the questions, such as 'Next Questions'. Try not to repeat questions that have already been asked.
- what subject is the users question about? use no more than 3 words.

{ai_response}
"""
    follow_up_prompt = ChatPromptTemplate.from_template(follow_up_template)
    follow_up_prompt.append(SystemMessage(content=format_instructions))
    return follow_up_prompt


class UserConversation:

    def __init__(
        self,
        conversation,
        ai_model: AILLMModels,
        search_client: VectorSearchService,
        sourcepage_field: str,
        content_field: str,
        settings: Settings
    ):
        self.ai_model = ai_model
        self.search_client = search_client
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        self.conversation = conversation
        self.settings = settings

    async def send_message(self, query_text: str) -> AsyncIterable[str]:
        model = self.ai_model.getModel()
        # add back in future version
        user_info = get_user_info()
        # Step 0: setup chain processors we will in multiple chains
        # Step 0.1: setup mongo backed memory
        raw_message_history = MongoDBChatMessageHistory(
            connection_string=self.settings.MONGO_CONN_STR or os.getenv("MONGO_CONN_STR"),
            database_name=self.settings.MONGO_DB or os.getenv("MONGO_DB"),
            collection_name=self.settings.RAW_MESSAGE_COLLECTION or os.getenv("RAW_MESSAGE_COLLECTION"),
            session_id=(self.conversation.id or None)
        )

        memory = ConversationBufferWindowMemory(
            k=self.settings.HISTORY_WINDOW_SIZE or 10,
            chat_memory=raw_message_history, 
            return_messages=True
        )

        # Step 0.2: create a memory runnable 
        # langchain 'runnables' documented here: https://api.python.langchain.com/en/latest/runnables/langchain_core.runnables.base.Runnable.html#
        loaded_memory = RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history"),
        )

        logger.info(f"loaded memory from conversation buffer: {loaded_memory}")
        # Step 1: Generate an optimized keyword search query based on history and current question
        chain : RunnablePassthrough = loaded_memory | get_optimized_keyword_prompt(query_text, user_info) | model
        chat_completion = await chain.ainvoke({"user_query": query_text, "user_info": user_info})
        step1Return = chat_completion.content
        if step1Return == "0":
            step1Return = query_text
            
        logger.info(f"generated search text: {step1Return}")

        # Step 3: Send the query to Azure Search
        r = self.search_client.getSearchClient().similarity_search(
            query=step1Return,
            k=3,
            search_type="similarity",
        )
        
        results = []
        #logger.info(f"got semantic search result: {r}")
        for doc in r:
            page_content = doc.page_content
            source = doc.metadata['source']
            results.append(f"Content: {page_content}\nSource: {source}")

            # Join all results into a single string, separated by a line break
        content = "\n\n".join(results)
        #logger.info(f"got vector database supplement: {content}")

        # step 4: do a GPT call with the request and documents
       
        # 4.1 setup message parser and configure model with callbacks
        model.callbacks = [StreamingParser(
            conversation=self.conversation, 
            user_question=query_text, 
            memory=memory)]
        
        # 4.2 create and run the chain

        answer_chain = loaded_memory | generate_gpt_prompt(user_info) | model 
        full_chain = {"ai_response": answer_chain} | generate_follow_up_prompt() | model
        
        task = asyncio.create_task(
            full_chain.ainvoke({"user_question": query_text, "sources": content})
        )
        
        callback = model.callbacks[0]
        
        try:
            async for line in callback.aiter():
                logger.info(f'yeilding line: {line}')
                yield dict(data=line)

        except Exception as e:
            logger.info(f"Caught exception: {e}")
            raise e
        except openai.error.APIConnectionError as e:
            logger.info(f"Caught APIConnectionError: {e}")
            raise e
        finally:
            try: 
                callback.conversation.save()
                callback.done.set()
            except Exception as e: 
                logger.info(f'caught exception finally {e}')
                raise e

        await task
