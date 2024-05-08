import json
example_data = [
    {
        "name": "Factors Influencing Degree Selection",
        "description": "Consideration of various factors like personal interests, career objectives, job market trends, and earning potential that influence the choice of a degree, major, or certificate.",
        "tags": "personal interests, career goals, job market, earning potential, degree choice",
        "label": "Topic"
    },
    # Include other examples as shown previously...
]

def evaluate_topic_node(question, example_data):

    prompt = f'''You are an acadmic advising assistant.  Your job is to populate a knowledge graph that 
    relates advising question to topics.  Given the user question '{question}', generate a new topic with 
    name, description, tags, and label based on the following examples: {json.dumps(example_data)}.  The 
    output must be in JSON using the same format as the examples.'''
    return prompt


