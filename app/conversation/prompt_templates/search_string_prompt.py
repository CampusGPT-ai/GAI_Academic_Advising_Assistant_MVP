
def get_search_prompt(user_info):
    return f''' Develop a semantic search string based on the university student profile information below.  The search
    string will be used to search an FAQ for question and answer pairs that are unique to the students academic background, financial and social circumstances, and interests. 
    If no personal user information is provided, assume the question is anonymous. 
    The search string must be natural and fluid to be suitable for a semantic search using vector embeddings.  It should have 
    enough detail and keywords to return relevant results.  Only return the search string.  Do not return additional information about your
    thought processes or reasoning.  \n
    [USER INFO]:\n
    {user_info}\n\n
    [YOUR RESPONSE]:\n
'''

def get_keyword_prompt(user_question, user_info):
        return f''' Develop a semantic search string based on the university student profile information below.  The search
    string will be used to search for documentation that answers the student's provided question, while also incorporating their unique person information such as academic background,
     financial and social circumstances, and interests. If no personal user information is provided, assume the question is anonymous. 
    The search string must be natural and fluid to be suitable for a semantic search using vector embeddings.  It should have 
    enough detail and keywords to return relevant results directly related to the user's question.  Only return the search string.  Do not return additional information about your
    thought processes or reasoning.  \n
    [USER QUESTION]:\n
    {user_question} \n\n
    [USER INFO]:\n
    {user_info}\n\n
    [YOUR RESPONSE]:\n
'''