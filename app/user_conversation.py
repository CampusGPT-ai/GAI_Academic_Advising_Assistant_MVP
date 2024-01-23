import openai, os
import asyncio

from operator import itemgetter
from typing import AsyncIterable
from cloud_services.gpt_models import AILLMModels
from cloud_services.vector_search import VectorSearchService
from langchain.schema import SystemMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain.memory.chat_message_histories import MongoDBChatMessageHistory
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from settings.settings import Settings
from conversation.streaming_parser import StreamingParser
from util.logger_format import CustomFormatter
import logging, sys

ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.handlers.clear()  
logger.addHandler(ch)  


def nonewlines(s: str) -> str:
    return s.replace('\n', ' ').replace('\r', ' ')


def get_optimized_keyword_prompt() -> ChatPromptTemplate:
    system_instructions = """
You are semantic search assistant that is part of the backend of a language model based chat bot tool.
Your job is to review the user information and question below, and craft a semantic search query that will be later converted to a vector and used in 
a similarity search against a large database of vectors in a nearest neighbor similarity search. 
The semantic query should be designed to return information that is a close match to the users question, with enough detail to inform the search, but not so much detail that the search will be unlikely to return a result. 
If possible, the query should be PERSONALIZED to the user by including relevant details from the users information, academic history and interests.  Use your best judgement on which personal attributes to include in the search query based on the topic and context. 
"""
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=(system_instructions)),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("User Profile: {user_info}\n\n User Question: {user_query}\n\n")
    ])
    return prompt


def generate_gpt_prompt(user_info) -> ChatPromptTemplate:
    # Start with the system message

    system_instructions = f"""
You are an academic advisor for university students.  Use the [CONTEXT] and [RESPONSE INSTRUCTIONS] below to answer student questions. \n\n
[CONTEXT]:\n
{user_info}
\n\n
[RESPONSE INSTRUCTIONS]:\n
- Provide concise answers.\n
- Include HTML markup in your response with headings, subheadings, break tags and hyperlink references as appropriate.  \n
- You have inherent knowledge about the campus, courses, and other academic information.  Answer questions as if this knowledge is innate to you while giving references to the sources of the information.\n
- Do not provide metadata about your thought processes or how you came to a response.  The student should not know you are a bot. \n
- When possible, use the information from the provided university sources.  \n
- If the user asks a generic question, and you do not have personalized information about that student, respond in a generic way.  For example, if the question is \"What courses do I need to graduate?\", but you do not know anything about the student, respond with generic, non-specific information about graduation requirements. \n
- If you do have personalized information about that student, use that information in your response when it makes sense to do so.  \n
- If you do not know the answer to a question, state in a friendly, professional way, that you do not have an answer and provide the user with information about a contact person or office to follow up with.  \n
- Reference each fact you use from a source using square brackets, e.g., [info1.txt]. Do not merge facts from different sources; list them separately. e.g. [info1.txt][info2.pdf].\n
- If the user's query pertains to classes or courses, and you have personalized information about the student, always reference and list the classes the student has previously taken.\n
- before you respond, self-check your answer and make sure it makes logical sense, and that recommended actions and hyperlinks are related to the question at hand.\n
- before you respond, check the hyperlinks provided as source references.  Make sure the link is actually correct for the citation.  
\n\n
"""

    json_return_reminder = """
    topic: what subject is the answer about? use no more than 3 words.
    Format the outut as JSON with the following keys and sepearate anwswer and topic with this character sequence '<<<<':
    topic: the topic of the conversation
    """
    #Return the answer as a text string and append the topic in JSON format following these examples. 
    #Separate the answer and the topic with a this character sequence '<<<<'.
    #response to user question { "topic": "conversation topic" }
    #response to user question2 { "topic": "conversation topic2" }

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=(system_instructions)),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template(
            "{user_question}\n\nSources:\n{sources}") 
    ])
    logger.info(f"generated prompt template: {prompt}")
    return prompt

def get_user_info(profile):
    my_classes = "No classes taken yet"
    
    if profile is not None and profile.academics is not None:
        major = profile.academics.get("Major")
        full_name = profile.full_name
        year = profile.academics.get("Academic Year")
        interests = ", ".join(profile.interests)
        demographics_ethnicity = profile.demographics.get("ethnicity")
        demographics_gender = profile.demographics.get("gender")
        classes_list = profile.courses
        
    if classes_list is not None and len(classes_list) > 0:
        my_classes = ", ".join(classes_list)
    
    message = f'''- Student name': {full_name} \n
    - Major: {major}\n
    - Year: {year}\n
    - Gender: {demographics_gender}\n
    - Ethnicity: {demographics_ethnicity}\n
    - Interests: {interests}
    - Classes taken: {my_classes}\n
    '''
    logger.info(f"user info: {message}")
    return message

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
        institution,
        user,
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
        self.institution = institution
        self.user = user
        self.conversation = conversation
        self.settings = settings

    async def send_message(self, query_text: str) -> AsyncIterable[str]:
        model = self.ai_model.getModel()
        if self.user:
            user_info = get_user_info(self.user)
        else: 
            user_info = 'no user selected'
        # Step 0: setup chain processors we will in multiple chains
        # Step 0.1: setup mongo backed memory
        raw_message_history = MongoDBChatMessageHistory(
            connection_string=self.settings.APPSETTING_MONGO_CONN_STR or os.getenv("APPSETTING_MONGO_CONN_STR"),
            database_name=self.settings.APPSETTING_MONGO_DB or os.getenv("APPSETTING_MONGO_DB"),
            collection_name=self.settings.APPSETTING_RAW_MESSAGE_COLLECTION or os.getenv("APPSETTING_RAW_MESSAGE_COLLECTION"),
            session_id=(self.conversation.id or None)
        )
        memory = ConversationBufferWindowMemory(
            k=self.settings.APPSETTING_HISTORY_WINDOW_SIZE or 10,
            chat_memory=raw_message_history, 
            return_messages=True
        )

        # Step 0.2: create a memory runnable 
        loaded_memory = RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history"),
        )
        logger.info(f"loaded memory from conversation buffer: {loaded_memory}")
        # Step 1: Generate an optimized keyword search query based on history and current question
        chain = loaded_memory | get_optimized_keyword_prompt() | model
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
            user=self.user, 
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
