def get_gpt_system_prompt(input_q,user_info, considirations):

    system_instructions = f"""
    You are a search agent assistant an academic advisor in answering student questions.  Decide if you have sufficient information to answer the students question below. \n
    if you are ready to decide, return "yes" and a detailed search query that will be used in a semantic vector search. \n
    If you are are missing import consideratons, return "no" and a follow up question to gather the missing information. \n
    Your response should be in JSON format and include the following fields: \n
    - "response": "yes" or "no" \n
    - "search_query": "detailed search query" \n
    - "follow_up_question": "follow up question" \n\n
    [QUESTION]:\n
    {input_q}
    \n\n
    It is important to consider the following information about the student before providing a response: \n
    [STUDENT INFORMATION]:\n
    {user_info} \n\n 

    If the user information is missing any of the below considerations, you should ask a follow up question to gather the missing information. \n
    [CONSIDERATIONS]:\n 
    {considirations} \n\n

    [YOUR RESPOSNE]:\n
"""
    
    return system_instructions