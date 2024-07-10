import json 
def get_gpt_classification_prompt(c,p):

    system_instructions = f"""
    You are a search agent assisting an academic advisor in answering student questions.  review the user input below and the user profile.  \n
    first determine if the user is asking a question or expressing a statement.  \n
    then search the users input text below to see if you can gather any of the below considerations that are NOT already in the user profile.  \n
    # User input may contain both questions and considerations.  \n
    # only return considerations that are not already in the user profile. \n
    # only return considerations that are explicitly stated in the user input.  If nothing is listed for a category, do not return that cateogry. \n
    # only include descriptive attributes or facts about the user as considerations, for example, hobbies, past academic performance, financial concerns, etc. \n
    # Do not include the question as a topic the user is interested in learning about as a consideration.  
    use the list of names and definitions, read the user input, compare against the user profile, and return newly categorized information in JSON format as follows:
    - "contains question:": "yes" or "no" \n
    - "contains considerations": "yes" or "no" \n
    [considerations list:
    - "name": "name of consideration" \n
    - "user information:" "user information" \n
    ]\n
    [USER PROFILE]:\n
    {p}
    [LIST OF CONSIDERATIONS]:\n
    {",".join(json.dumps(c))}
    \n\n
"""
    
    return system_instructions, ['contains considerations']