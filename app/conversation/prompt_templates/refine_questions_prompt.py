
def get_questions_prompt(user_info, questions):
    return f''' below is a list of questions.  trim duplicates from the list.  
    Return the top 6 questions that would be most relevant to a university student based on the information provided below.  \n
    do not explain your reasoning or thought process in your response, just provide a list of questions \n
    the list of questions should be new line separated, do not include numbers or bullet points in your answer. \n
    [STUDENT INFO]:\n
    {user_info}\n\n
    [QUESTION]:\n
    {questions}\n\n
    [YOUR RESPONSE]
'''
