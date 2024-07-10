from cloud_services.openai_response_objects import Message

def summarize_chunks(c):
            system_content = ('''
You are an NLP agent.  Your job is to convert raw text into semantic search strings.  \n\n
For the text below identify facts about people, places, entities, events, advice, recommendations, actions, or any other topics you can think of.  \n
For each fact you find, list the fact in a short paragraph.  \n
- The paragraph should include the fact itself and all additional context that will help improve semantic search results using cosign similarity search on the embedded data. \n
- Each paragraph should stand alone, without relying on knowledge of preceeding text to make sense. \n  
- Repeat major topics, themes, and other facts from the body of the text for each paragraph. \n
- if the content includes a date ALWAYs include the year in the paragraph. \n
- If the content includes a location, ALWAYS include the address in the paragraph. \n
- If the content includes a date, always include the year if possible, you may need to check the surrounding context to determine the year. \n
Create as many paragraphs for as many facts as you possibly can.  \n
always include specific dates if they are provided. \n
Always include addresses and contact information if it is provided.  \n
Do not number the paragraphs.  Separate each paragraph with a double line break.  '''
r"""\n\n""")

            return (
                [
            Message(role='system', content=system_content),
            Message(role='user',content=c)
        ]
            )


def summarize_catalog(c):
    system_content = ('''
Please summarize the catalog information provided. Include all essential details about the course or program, such as the course 
                      title, course code, credit hours, prerequisites, description, and any logistical information (e.g., lab hours, 
                      frequency of offering). Highlight any additional relevant information that pertains to the course or program 
                      structure. \n\n''')

    return (
            [
        Message(role='system', content=system_content),
        Message(role='user',content=c)
    ]
        )

 
def summarize_catalog_simple(c):
    system_content = ('''
Please summarize the information provided.  If the information appears to be a list of courses, summarize each course description individually.  Don't leave important information out. n\n''')

    return (
            [
        Message(role='system', content=system_content),
        Message(role='user',content=c)
    ]
        )

 