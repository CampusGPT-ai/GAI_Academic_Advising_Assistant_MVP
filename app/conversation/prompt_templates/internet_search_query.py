def get_gpt_search_prompt(p):

    system_instructions = f"""
    create a list of search strings that will be used to conduct an internet search to return relevant websites based on the below information. \n
    The websites will be used as resources for a student in the context of academic advising.  \n
    return a json object with one field, which is a list of search strings. The feild should be called "search_strings" and the value should be a list of strings in square brackets. \n
    the list should contain no more than 3 search strings.  choose the most relevant keywords and phrases.  \n
    If possible, include the university name in the search strings to ensure the results are specific to the university. \n
    each search string should be significantly different from the others to avoid duplicate search results. \n
    [INFORMATION TO CONSIDER]:\n
    {p}
    [YOUR RESPONSE]:\n
"""
    
    return system_instructions, ['search_strings', 'search strings', 'search terms']