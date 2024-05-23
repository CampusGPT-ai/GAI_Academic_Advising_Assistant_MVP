def create_prompt_for_new_considerations_and_outcomes_relationships(new_node_info, existing_considerations_outcomes):
    prompt = f'''You are an acadmic advising assistant.  Your job is to populate a knowledge graph that relates advising question to topics. Considering the new topic {new_node_info.get('name')}: {new_node_info.get('description')} and existing mapped nodes {existing_considerations_outcomes}, suggest any new considerations and outcomes necessary. 
    if you do suggest new considerations or new outcomes, create the data necessary to map these nodes as relationships to the topic node.  \n\n
    [RESPONSE INSTRUCTIONS]: \n
    # Considerations can be mapped as IS_CONSIDERATION_FOR where the consideration is the 'from' node and the topic is the 'to' node.  \n
    # topic nodes are mapped to outcome nodes as risks and opportunities using IS_RISK_OF and IS_OPPORTUNITY_FOR, where the topic is the 'from' node and the outcome is the 'to' node.  \n
    # A single outcome node can be listed as both a risk an opportunity. \n
    # IMPORTANT: The output must be in JSON format with the following structure:''' + r''' {{"name": "topic_name", "relations": [{"name": "node_name", "type": "relationship_type"}]}}. \\n\\n'''
    return prompt

def create_prompt_for_new_considerations_and_outcomes(new_node_info, existing_considerations_outcomes):
    prompt = f'''You are an acadmic advising assistant.  Your job is to populate a knowledge graph that relates advising question to topics. 
    Considering the new topic {new_node_info.get('name')}: {new_node_info.get('description')} and existing mapped nodes {existing_considerations_outcomes}, suggest any new considerations and outcomes necessary. 
    [RESPONSE INSTRUCTIONS]: \n
    # Considerations represent attributes of a student that are important to consider when advising.  \n
    # Considerations will be used for query expansion and to form follow up questions and prompt the student for more information, prior to answers being generated.  \n
    # Outcomes are risks, opportunities, or both, related to an adivising topics.  
    # These outcomes will be used prompt the student to explore additional topics prior to generating an answer.  \n
    # A single outcome node can be listed as both a risk an opportunity.  this means you will list it twice in the output with different relationships. \n
    # your final output will be a list of considerations and outcomes that are necessary for the new topic.  \n
    # For both outcomes and considerations, you will generate a description that will be used for semantic search to match topics and user inputs to items. \n
    # IMPORTANT: The output must be in JSON format with the following structure:''' + r''' {'considerations OR outcomes': \[{"name": "item_name", "label": "topic OR outcome", "description": "semantically complete descriptive text", "relationship_to_topic": "ONE OF IS_CONSIDERATION_FOR, IS_OPPORTUNITY_FOR, or IS_RISK_OF", "tags": "keyword tags used for keyword search".\]}} \\n\\n'''
    return prompt

