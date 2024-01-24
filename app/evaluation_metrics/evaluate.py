import dotenv
dotenv.load_dotenv()

import cloud_services.llm_services as llm
import os, openai
from typing import List
from cloud_services.openai_response_objects import Message, ChatCompletion
# setup openai connection
import logging, sys
from trulens_eval import Tru
from trulens_eval.tru_custom_app import instrument
from cloud_services.azure_cog_service import AzureSearchService



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout)  # Ensures logs go to stdout
    ]
)

VECTOR_FIELD = 'content_vector'
VECTOR_FIELDS = ['content_vector']

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_VERSION = os.getenv("OPENAI_API_VERSION")
OPENAI_ENDPOINT= os.getenv("OPENAI_ENDPOINT")
OPENAI_DEPLOYMENT = os.getenv("DEPLOYMENT_NAME")
OPENAI_MODEL = os.getenv("MODEL_NAME")
EMBEDDING = os.getenv("EMBEDDING")
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT2")
SEARCH_API_KEY= os.getenv("SEARCH_API_KEY2")
SEARCH_INDEX_NAME=os.getenv("SEARCH_INDEX_NAME2")
SYSTEM_TEXT = '''prompt'''
EMBEDDING_DEPLOYMENT = os.getenv("EMBEDDING")

openai.api_key = OPENAI_KEY
openai.api_version = OPENAI_VERSION
openai.base_url = OPENAI_ENDPOINT
openai.azure_endpoint = ''
openai.api_type = 'azure'



class EvaluateRAG:
    def __init__(self):
        self.azure_llm = llm.get_llm_client(api_type='azure',
                                api_version=OPENAI_VERSION,
                                endpoint=OPENAI_ENDPOINT,
                                model=OPENAI_MODEL,
                                deployment=OPENAI_DEPLOYMENT,
                                embedding_deployment=EMBEDDING_DEPLOYMENT)
        
        self.search_client = AzureSearchService(SEARCH_ENDPOINT,
                                                SEARCH_INDEX_NAME,
                                                self.azure_llm,
                                                SEARCH_API_KEY)
    
    def query_ai(self, messages: List[Message]): 
        return self.azure_llm.chat(messages)
    
    @instrument
    def retrieve(self,query: str) -> list:
        results = self.search_client.simple_search(query,'content_vector',['content'])
        few_shot = self.search_client(query,'questions_vector',['questions','followups','content','id'])
        return results[:2], few_shot
    
    @instrument
    def generate_completion(self,query, context_str: list) -> str:
        
        def get_prompt():
            user_content =(
                    f"""
You are an academic advisor for university students at the University of Central Florida.  Use the [STUDENT CONTEXT], [INFORMATION CONTEXT], and [RESPONSE INSTRUCTIONS] below to answer student questions. \n\n
[STUDENT CONTEXT]:\n
Student: Tiffany Tallahasee
Interests:\n
Student Government, Volunteer UCF, Bright Futures Scholarship Recipient\n
Academics:\n
Year: 2, Major: Computer Engineering\n
Course History:\n
EGS1006C, EGN1007C, EGN3420, COT3100C, COP3502C, COP3503C, COP3330, EEL4768, COP4600\n
[INFORMATION CONTEXT]: \n
{context_str}
\n\n
[RESPONSE INSTRUCTIONS]:\n
- IMPORTANT: Provide specific, practical, and personalized examples in your responses. 
- Provide direct, concise answers.  Eliminate verbosity.\n
- write with an active voice with the subject at the forefront - ie instead of saying "it would be helpful to have x" say, "You need x", etc \n
- Respond at a ninth grade reading level. \n
- Respond in a friendly, encouraging tone. \n
- Use the information from the provided university sources.  \n
- If you have personalized information about a student that is related to the question, use that information in your response.  \n
- If you do not know the answer to a question, state that you do not have an answer.  If possible, provide the user with information about a contact person or office to follow up with.  If there is no contact person in the context for the question, point the person to the office of academic advising. \n
- Reference each fact you use from a source using square brackets, e.g., [info1.txt]. Do not merge facts from different sources; list them separately. e.g. [info1.txt][info2.pdf].\n
- Think step-by-step.  First compose a response using these rules, then check your response against each rule.  Make changes if necessary.  Return the response. 
\n\n
{query}""" 
            )
            return (
                [
            Message(role='system', content=SYSTEM_TEXT),
            Message(role='user',content=user_content)
        ]
            )
    
        
        messages = get_prompt()
        result : ChatCompletion = self.azure_llm.chat(messages)
        return result.choices[0].message
    
    @instrument
    def query(self, query: str) -> str: 
        context_str, example_questions = self.retrieve(query)
        completion = self.generate_completion(query, context_str)
        return completion
    
from trulens_eval import Feedback, Select
from trulens_eval.feedback import Groundedness
from trulens_eval.feedback.provider.openai import OpenAI as fOpenAI
import numpy as np

# Initialize provider class
fopenai = fOpenAI()

grounded = Groundedness(groundedness_provider=fopenai)

# Define a groundedness feedback function
f_groundedness = (
    Feedback(grounded.groundedness_measure_with_cot_reasons, name = "Groundedness")
    .on(Select.RecordCalls.retrieve.rets.collect())
    .on_output()
    .aggregate(grounded.grounded_statements_aggregator)
)

# Question/answer relevance between overall question and answer.
f_qa_relevance = (
    Feedback(fopenai.relevance_with_cot_reasons, name = "Answer Relevance")
    .on(Select.RecordCalls.retrieve.args.query)
    .on_output()
)

# Question/statement relevance between question and each context chunk.
f_context_relevance = (
    Feedback(fopenai.qs_relevance_with_cot_reasons, name = "Context Relevance")
    .on(Select.RecordCalls.retrieve.args.query)
    .on(Select.RecordCalls.retrieve.rets.collect())
    .aggregate(np.mean)
)

evaluation_questions = ["Are there any tutors, mentors, or advisors who can help me?","How many hours do I need to take to keep my financial aid?","What classes do i need to take to graduate?","Who is my advisor?","My roommate seems depressed, what should I do?","I was harassed at a party last night, what should I do?","What are my career options after I graduate?","What history courses are available for my minor?","Are there any language courses or clubs I can join?","Where can I find information on outdoor activities or clubs?","Are there any watersports activities or clubs at UCF?","How can I find research opportunities in my field?","Where can I get information on financial aid?","Where can I find tutoring for my major?","How can I join a study group?","How do I sign up for next semester's classes?","Are there any clubs for women in technology?","Where can I find resources on entrepreneurship?","How can I get involved in singing on campus?","Where can I access health and wellness resources?","How can I find internships related to my major?","How do I apply for work-study?","Are there study abroad programs I can participate in?","How do I apply for housing?"]
 
evaluation_questions_short = ["Are there any tutors, mentors, or advisors who can help me?","How many hours do I need to take to keep my financial aid?"]
        

if __name__ == "__main__":
    tru = Tru()
    rag = EvaluateRAG()
    
    from trulens_eval import TruCustomApp
    for n in evaluation_questions_short:
        tru_rag = TruCustomApp(rag,
        app_id = 'ucf-index-v2-question_vector',
        feedbacks = [f_groundedness, f_qa_relevance, f_context_relevance])
        
        with tru_rag as recording:
                rag.query(n)
        
        tru.get_leaderboard(app_ids=["ucf-index-v2-question_vector"])
        tru.run_dashboard()
    