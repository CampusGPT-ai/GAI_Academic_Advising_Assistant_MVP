from cloud_services.llm_services import AzureLLMClients, get_llm_client
from settings.settings import Settings
from user.get_user_info import UserInfo
from cloud_services.kg_neo4j import Neo4jSession
from conversation.retrieve_docs import SearchRetriever
from conversation.prompt_templates.kick_back_prompt import get_gpt_system_prompt as kick_back_prompt
from conversation.prompt_templates.gpt_qa_prompt import get_gpt_system_prompt as gpt_qa_prompt
from cloud_services.openai_response_objects import Message

settings = Settings()

azure_llm_client : AzureLLMClients = get_llm_client(api_type='azure',
                                                    api_version=settings.OPENAI_API_VERSION,
                                                    endpoint=settings.AZURE_OPENAI_ENDPOINT,
                                                    model=settings.GPT35_MODEL_NAME,
                                                    deployment=settings.GPT35_DEPLOYMENT_NAME,
                                                    embedding_deployment=settings.EMBEDDING)

#step 1: get the user question and user ID
#will just proxy this for testing (this will be a route)
def get_user_question():
    #get the user question
    response = "What internships should I apply for?"
    id = "A_iXG9LQjG86PTY1sgG-Sm9JO3IbMlliRkZok3BhT8I"
    non_session_id = '70fcb1b3-0d35-4370-888b-8f456f353560'
    return response, id

#step 2: query the user profile and return considerations
def get_user_considerations(user_id):
    user = UserInfo(user_id)
    considerations = user.get("considerations")
    return considerations

#step 3: query the graph and return considerations
def get_graph_considerations(user_question):
    finder = Neo4jSession(settings.N4J_URI, settings.N4J_USERNAME, settings.N4J_PASSWORD)
    related_topic = finder.find_similar_nodes(user_question)
    considerations = finder.construct_and_execute_query(related_topic, 'Consideration','IS_CONSIDERATION_FOR')
    finder.close()  
    return considerations

#step 3.5: match considerations from graph to considerations from profile
def match_considerations(considerations_from_profile, considerations_from_graph):
    missing_considerations = []
    for consideration in considerations_from_graph:
        if consideration not in considerations_from_profile:
            missing_considerations.append(consideration)
    return missing_considerations

#step 3.75: query search index with best information based on current considerations
def query_search_index(user_question, considerations):
    retriever = SearchRetriever.with_default_settings()
    full_query = f"{user_question} {considerations}"
    results = retriever.retrieve_content(full_query, n=10)
    return query_search_index

#step 3.9: query LLM to respond with rag.  Keep response in memory. 
def query_llm(response):
    #query the LLM
    #return the response
    return "response"

#step 4: create prompt to GPT to compare the considerations and determine if follow up is necessary.  If follow up is necessary, return the follow up question to the user
def create_gpt_prompt(user_question, user_info, considerations):
    # Start with the system message
    rag_instructions = gpt_qa_prompt(user_info, "")
    system_instructions = kick_back_prompt(user_question, user_info, considerations)
    return Message(role="system",content=system_instructions)
#step 5: return the response to the user
def return_response(response):
    #return the response
    return response

#step 6: await response to prompt?  how to flag this in the front end as a return
def await_response(response):
    #return the response
    return response

#step 7: update user profile with the new user information
def update_user_profile(user_id, user_info):
    #update the user profile
    return "user profile updated"
