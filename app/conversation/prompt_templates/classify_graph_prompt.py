def get_gpt_classification_prompt(c,p):

    system_instructions = f"""
    search the users input text below to see if you can gather any of the below considerations that are NOT already in the user profile.  \n
    only return considerations that are not already in the user profile. \n
    use the list of names and definitions, read the user input, compare against the user profile, and return newly categorized information in JSON format as follows:
    - "contains considerations": "yes" or "no" \n
    [considerations list:
    - "name": "name of consideration" \n
    - "user information:" "user information" \n
    ]\n
    [USER PROFILE]:\n
    {p}
    [LIST OF CONSIDERATIONS]:\n
    {c}
    \n\n
"""
    
    return system_instructions, ['contains considerations', 'name', 'user information']