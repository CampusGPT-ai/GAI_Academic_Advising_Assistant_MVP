def evaluate_relevance_of_existing_nodes(new_node_info, description, existing_nodes):
    prompt = f'''You are an acadmic advising assistant.  Your job is to populate a knowledge graph that relates advising question to topics. Assess if the following existing nodes are directly related to the new topic {new_node_info}: {description}.  Existing nodes: {existing_nodes}.  
    If the existing nodes are very relevant, create the data necessary to map these nodes as relationships to the topic node. nodes should be mapped to the topic if the consideration or outcomes is directly related to the topic and description at hand.  
    Do not map the node if it nonly somewhat related.  \n\n
    [RESPONSE INSTRUCTIONS]: \n
    - Considerations can be mapped as IS_CONSIDERATION_FOR where the consideration is the 'from' node and the topic is the 'to' node.  \n
    - topic nodes are mapped to outcome nodes as risks and opportunities using IS_RISK_OF and IS_OPPORTUNITY_FOR, where the topic is the 'from' node and the outcome is the 'to' node.  \n
    - A single outcome node can be listed as both a risk an opportunity. \n
    - IMPORTANT: The output must be in JSON format with the following structure:''' + r''' {{"name": "topic_name", "relations": [{"name": "node_name", "type": "relationship_type"}]}}. \\n\\n'''
    return prompt
