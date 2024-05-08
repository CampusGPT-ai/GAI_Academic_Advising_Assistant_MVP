def create_prompt_for_new_considerations_and_outcomes(new_node_info, existing_considerations_outcomes):
    prompt = f'''You are an acadmic advising assistant.  Your job is to populate a knowledge graph that relates advising question to topics. Considering the new topic {new_node_info.get('name')}: {new_node_info.get('description')} and existing mapped nodes {existing_considerations_outcomes}, suggest any new considerations and outcomes necessary. 
    if you do suggest new considerations or new outcomes, create the data necessary to map these nodes as relationships to the topic node.  \n\n
    [RESPONSE INSTRUCTIONS]: \n
    - Considerations can be mapped as IS_CONSIDERATION_FOR where the consideration is the 'from' node and the topic is the 'to' node.  \n
    - topic nodes are mapped to outcome nodes as risks and opportunities using IS_RISK_OF and IS_OPPORTUNITY_FOR, where the topic is the 'from' node and the outcome is the 'to' node.  \n
    - A single outcome node can be listed as both a risk an opportunity. \n
    - IMPORTANT: The output must be in JSON format with the following structure:''' + r''' {{"name": "topic_name", "relations": [{"name": "node_name", "type": "relationship_type"}]}}. \\n\\n'''
    return prompt
