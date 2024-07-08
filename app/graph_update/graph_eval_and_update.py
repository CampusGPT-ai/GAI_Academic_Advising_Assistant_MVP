from settings.settings import Settings
from cloud_services.kg_neo4j import Neo4jSession
from threading import Thread
import json
from data.graph_vector import GraphVector
from queue import Queue
from conversation.run_chat import QueryLLM
from graph_update.prompt_templates.evaluate_matching_considerations import evaluate_relevance_of_existing_nodes
from graph_update.prompt_templates.generate_new_relationships import create_prompt_for_new_considerations_and_outcomes
from graph_update.prompt_templates.generate_new_topic import evaluate_topic_node
settings = Settings()
import logging
logger = logging.getLogger(__name__)
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
    
    #TODO: I'm not structuring this corrcetly - i need to add outcomes and consideratiosn before I can map them. 
    def identify_new_considerations_outcomes(self, new_node_name, related_nodes):
        prompt = create_prompt_for_new_considerations_and_outcomes(new_node_name, related_nodes)
        template, _ = self.llm_client.create_prompt_template(prompt)
        response = self.llm_client.run_llm(template)
        return response

    def parse_llm_response_and_add_node(self,response, node_type='Topic'):
        new_node_data = response
        self.finder.add_node(new_node_data.get('name'), new_node_data.get('description'), new_node_data.get('tags'),node_type)
    
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
        return related_nodes_info
    
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
    
    def add_new_topic_node(self, topics):
        new_topics = self.find_new_topics(topics)
        logger.info(f'found new topics: {new_topics}')
        self.parse_llm_response_and_add_node(new_topics)
        GraphVector().add_single_vector(new_topics.get('name'))
        return new_topics
    
    def add_new_relationships(self, topics, new_topics):
        related_nodes = self.find_and_return_related_nodes(topics)
        logger.info(f'related nodes: {related_nodes}')
        relationships = self.identify_relationships(new_topics.get('name'), new_topics.get('description'), related_nodes)
        logger.info(f'found relationships: {relationships}')
        self.add_relationships_to_graph(new_topics.get('name'), relationships.get('relations'))
        return relationships
    
    def add_new_considerations_outcomes(self, new_topics, relationships):
        new_considerations_outcomes = self.identify_new_considerations_outcomes(new_topics, relationships.get('relations'))
        logger.info(f'found new considerations and outcomes: {new_considerations_outcomes}')
        for consideration in new_considerations_outcomes.get('considerations'):
            try: 
                self.finder.add_node(consideration.get('name'), consideration.get('description'), consideration.get('tags'), 'Consideration')
                GraphVector().add_single_vector(consideration.get('name'))
                self.finder.add_relationship(consideration.get('name'), new_topics.get('name'), 'IS_CONSIDERATION_FOR')
            except Exception as e:
                logger.error(f'failed to add consideration {consideration} with error {str(e)}')
                continue
        for outcome in new_considerations_outcomes.get('outcomes'):
            try:
                self.finder.add_node(outcome.get('name'), outcome.get('description'), outcome.get('tags'), 'Outcome')
                GraphVector().add_single_vector(outcome.get('name'))
                self.finder.add_relationship(new_topics.get('name'), outcome.get('name'), outcome.get('relationship_to_topic'))
            except Exception as e:
                logger.error(f'failed to add outcome {outcome} with error {str(e)}')
                continue
    
    def orchestrate_graph_update(self, topics):
        new_topics = self.add_new_topic_node(topics)
        relationships = self.add_new_relationships(topics, new_topics)
        logger.info(f'adding new considerations and outcomes to graph')
        self.add_new_considerations_outcomes(new_topics, relationships)
    
    def orchestrate_graph_update_existing_topic(self, topics, new_topics):
        relationships = self.add_new_relationships(topics, new_topics)
        self.add_new_considerations_outcomes(new_topics, relationships)


    async def orchestrate_graph_update_async(self, topics):
        if topics and topics != [] and topics != '':
            logger.info('orchestrating graph update')
            import asyncio
            await asyncio.to_thread(self.orchestrate_graph_update(topics))

    def import_from_csv(self, file_path):
        import csv
        csv_file_path = file_path
        list_of_dicts = []
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Append each row as a dictionary to the list
                list_of_dicts.append({
                    'name': row['name'],
                    'description': row['description']
        })
        
        return list_of_dicts
    
    def add_new_topic(self, new_topics):
        from conversation.run_graph import GraphFinder
        
        for topic in new_topics:
            graph = GraphFinder(self.user_session, topic.get('description'))
            topics = graph.get_topic_list_from_question()
            self.orchestrate_graph_update_existing_topic(topics, topic)
        

    def import_new_graph_topics(self, topic_path, consideration_path, relationships_path):

        topics = self.import_from_csv(topic_path)
        considerations = self.import_from_csv(consideration_path)
        relationships = self.import_from_csv(relationships_path)
        self.import_new_considerations(considerations, relationships)

        for new_topics in topics.get():
            related_topics = GraphFinder(mock_user_session, new_topics.get('name')).get_topic_list_from_question()
            self.parse_llm_response_and_add_node(new_topics) #add topic node
            GraphVector().add_single_vector(new_topics.get('name')) #add vector for topic
            related_nodes = self.find_and_return_related_nodes(related_topics)
            relationships = self.identify_relationships(new_topics.get('name'), new_topics.get('description'), related_nodes)
            self.add_relationships_to_graph(new_topics.get('name'), relationships.get('relations'))
            new_considerations_outcomes = self.identify_new_considerations_outcomes(new_topics, relationships.get('relations'))
            self.add_relationships_to_graph(new_topics.get('name'), new_considerations_outcomes.get('relations'))
            
    def import_new_considerations(self, considerations, relationships):
        for consideration in considerations:
            self.finder.add_node(consideration.get('name'), consideration.get('description'), consideration.get('tags'), 'Consideration')
            GraphVector().add_single_vector(consideration.get('name'))


    def init_neo4j(self):
        if self.finder == None:
            self.finder = Neo4jSession(settings.N4J_URI, settings.N4J_USERNAME, settings.N4J_PASSWORD)
        return
    
if __name__ == '__main__':
    from pathlib import Path
    import json, csv
    from data.models import UserSession
    from conversation.run_graph import GraphFinder
    USER_QUESTION = "Entrepreneurship Workshops and Seminars"
    relative_path = Path('./app/data/sample_questions.json')

    with relative_path.open(mode='r') as file:
        mock_questions = json.load(file)

    session_path = Path('./app/data/mock_user_session.json')
    with session_path.open(mode='r') as file:
        mock_user_session : UserSession = UserSession(**json.load(file))
    n4j = NodeEditor(mock_user_session, USER_QUESTION)

    
    new_topics = n4j.import_from_csv('/Users/marynelson/Desktop/new_topics_list.csv')
    n4j.add_new_topic([{'name':'Entrepreneurship Workshops and Seminars', 'description':'Entrepreneurship Workshops and Seminars'}])


 #   if topics[0].get('score') < 0.9:
 #      print('adding new topics and relationships for low scoring match')
  #      finder = NodeEditor(mock_user_session, USER_QUESTION)
  #      finder.init_neo4j()
 #       finder.orchestrate_graph_update(topics)
 #  else:
 #       print('high scoring match returned from graph')
  #      print({'name': topics[0].get('name'), 'score': topics[0].get('score')})





