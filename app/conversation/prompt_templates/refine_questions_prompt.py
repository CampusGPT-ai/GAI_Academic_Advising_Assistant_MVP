
def get_questions_prompt(user_info,history):
    return f''' You are an experienced academic advisor. \n
    use the student information below to anticipate a list of 4 questions that this student might ask you.\n
    First, review the student information and come up with a list of questions that might be useful for the student to ask you. \n
    Then, review the conversation topic history.  Eliminate any questions that have fall into the topics already discussed. \n
    If you don't have any student information, come up with commonly asked collegiate advising questions, again taking the topic history into account.\n
    do not include any additional labels or text, just the list of questions. \n
    Use the student's conversation history to anticipate the questions. while, avoiding questions that would have been discussed in previous conversations. \n
    return questions in JSON format as follows:
    - "questions": [your list of questions] \n
    \n\n
    [CONVERSATION TOPIC HISTORY]: \n
    {history}\n\n
    [STUDENT INFO]:\n
    {user_info}\n\n
    [YOUR RESPONSE]
''', ['questions']
