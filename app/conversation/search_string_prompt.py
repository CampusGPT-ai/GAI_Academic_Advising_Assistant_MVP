
def get_prompt(user_info):
    return f''' Develop a semantic search string based on the university student profile information below.  The search
    string will be used to search an FAQ for question and answer pairs that are unique to the students academic background, financial and social circumstances, and interests. 
    The search string must be natural and fluid to be suitable for a semantic search using vector embeddings.  It should have 
    enough detail and keywords to return relevant results.  Only return the search string.  Do not return additional information about your
    thought processes or reasoning.  \n
    [USER INFO]:\n
    {user_info}\n\n
    [YOUR RESPONSE]:\n
'''
