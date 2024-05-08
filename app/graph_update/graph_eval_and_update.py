from settings.settings import Settings
from cloud_services.kg_neo4j import Neo4jSession
from threading import Thread
import json
from conversation.run_chat import QueryLLM
from graph_update.prompt_templates.evaluate_matching_considerations import evaluate_relevance_of_existing_nodes
from graph_update.prompt_templates.generate_new_relationships import create_prompt_for_new_considerations_and_outcomes
from graph_update.prompt_templates.generate_new_topic import evaluate_topic_node
settings = Settings()
uri = settings.N4J_URI
username = settings.N4J_USERNAME
password = settings.N4J_PASSWORD


class NodeEditor:
    def __init__(self, user_session, user_question):
        self.user_question = user_question
        self.user_session = user_session
        self.user_id = user_session.user_id
        self.finder = None
        self.llm_client = QueryLLM(user_session)
        self.init_neo4j()
    
    def find_new_topics(self, examples):
        prompt = evaluate_topic_node(self.user_question, json.dumps(examples))
        template, _ = self.llm_client.create_prompt_template(prompt)
        response = self.llm_client.run_llm(template)
        return response
    
    def identify_new_considerations_outcomes(self, new_node_name, related_nodes):
        prompt = create_prompt_for_new_considerations_and_outcomes(new_node_name, related_nodes)
        template, _ = self.llm_client.create_prompt_template(prompt)
        response = self.llm_client.run_llm(template)
        return response

    def parse_llm_response_and_add_node(self,response):
        new_node_data = response
        self.finder.add_node(new_node_data.get('name'), new_node_data.get('description'), new_node_data.get('tags'),'Topic')
    
    def find_and_return_related_nodes(self,topics):
        related_nodes_info = []
        for node in topics:
            considerations = self.finder.query_considerations(node.get('name'), 'Consideration', 'IS_CONSIDERATION_FOR')
            opportunities = self.finder.query_outcomes('IS_OPPORTUNITY_FOR', node.get('name'))
            risks = self.finder.query_outcomes('IS_OPPORTUNITY_FOR', node.get('name'))
            related_nodes_info.append({
                "name": node.get('name'),
                "considerations": considerations,
                "risks": risks,
                "opportunities": opportunities
            })
        return json.dumps(related_nodes_info)
    
    def identify_relationships(self, name, description, examples):
        prompt = evaluate_relevance_of_existing_nodes(name, description, examples)
        template, _ = self.llm_client.create_prompt_template(prompt)
        response = self.llm_client.run_llm(template)
        return response
    
    def add_relationships_to_graph(self, new_node_name, relevant_nodes):
        for relation in relevant_nodes:
            if relation.get('type') == 'IS_CONSIDERATION_FOR':
                self.finder.add_relationship(relation.get('name'), new_node_name, relation['type'])
            else:
                self.finder.add_relationship(new_node_name, relation.get('name'), relation['type'])


    def add_new_nodes_to_graph(self, new_considerations_outcomes):
        considerations_outcomes_data = json.loads(new_considerations_outcomes)
        for item in considerations_outcomes_data:
            self.finder.add_node(item['name'], item['description'], item['tags'], item['label'])
            self.finder.add_relationship(new_node_name, item['name'], item['relationship_type'])

    def query_outcomes(self, relationship_type, node_names):
        query = f"""
        MATCH (t:Topic)-[:`{relationship_type}`]->(o:Outcome)
        WHERE t.name = $node_name
        RETURN o
        """
        parameters = {'node_name': node_names, 'relationship_type': relationship_type}
        return self.run_query(query, parameters)
        

    def query_considerations(self, node_names, node_type, relationship_type):
    # Construct the query string dynamically using safe methods
        matches = []
        query = f"""
        MATCH (c:`{node_type}`)-[:`{relationship_type}`]->(t:Topic {{name: "{node_names}"}})
        RETURN c
        """
        return self.run_query(query)
    
    def orchestrate_graph_update(self, topics):
        from data.graph_vector import GraphVector
        new_topics = self.find_new_topics(topics)
        self.parse_llm_response_and_add_node(new_topics)
        GraphVector().add_single_vector(new_topics.get('name'))
        related_nodes = self.find_and_return_related_nodes(topics)
        relationships = self.identify_relationships(new_topics.get('name'), new_topics.get('description'), related_nodes)
        self.add_relationships_to_graph(new_topics.get('name'), relationships.get('relations'))
        new_considerations_outcomes = self.identify_new_considerations_outcomes(new_topics, relationships.get('relations'))
        self.add_relationships_to_graph(new_topics.get('name'), new_considerations_outcomes.get('relations'))

    async def orchestrate_graph_update_async(self, topics):
        import asyncio
        await asyncio.to_thread(self.orchestrate_graph_update(topics))

    def init_neo4j(self):
        if self.finder == None:
            self.finder = Neo4jSession(settings.N4J_URI, settings.N4J_USERNAME, settings.N4J_PASSWORD)
        return
    
if __name__ == '__main__':
    from pathlib import Path
    import json, csv
    from data.models import UserSession
    from conversation.run_graph import GraphFinder
    from data.graph_vector import GraphVector
    USER_QUESTION = "My roommate seems depressed.  What should I do?"
    relative_path = Path('./app/data/sample_questions.json')

    with relative_path.open(mode='r') as file:
        mock_questions = json.load(file)

    session_path = Path('./app/data/mock_user_session.json')
    with session_path.open(mode='r') as file:
        mock_user_session : UserSession = UserSession(**json.load(file))
    topics = GraphFinder(mock_user_session, USER_QUESTION).get_topic_list_from_question()
    if topics[0].get('score') < 0.9:
        print('adding new topics and relationships for low scoring match')
        finder = NodeEditor(mock_user_session, USER_QUESTION)
        finder.init_neo4j()
        finder.orchestrate_graph_update(topics)
    else:
        print('high scoring match returned from graph')
        print({'name': topics[0].get('name'), 'score': topics[0].get('score')})





