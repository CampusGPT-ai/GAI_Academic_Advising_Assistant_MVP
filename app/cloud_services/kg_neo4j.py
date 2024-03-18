from neo4j import GraphDatabase
from neo4j.graph import Relationship
import re
import pandas as pd
from evaluation_metrics.nlp import extract_keywords
from settings.settings import Settings
from cloud_services.llm_services import AzureLLMClients, get_llm_client

settings = Settings()
uri = settings.N4J_URI
username = settings.N4J_USERNAME
password = settings.N4J_PASSWORD

azure_llm_client : AzureLLMClients = get_llm_client(api_type='azure',
                                                    api_version=settings.OPENAI_API_VERSION,
                                                    endpoint=settings.AZURE_OPENAI_ENDPOINT,
                                                    model=settings.GPT35_MODEL_NAME,
                                                    deployment=settings.GPT35_DEPLOYMENT_NAME,
                                                    embedding_deployment=settings.EMBEDDING)

class Neo4jSession:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def find_similar_nodes(self,text,index='topic_index'):
        query_vector = azure_llm_client.embed_to_array(text)

        with self.driver.session() as session:
 
            result = session.run("""
                CALL db.index.vector.queryNodes('topic_index', 1, $queryVector)
                YIELD node AS similarDescription, score
            """, parameters={'queryVector': query_vector})

            for record in result:
                return record['similarDescription']['name']
        

    def construct_and_execute_query(self, node_names, node_type, relationship_type):
    # Construct the query string dynamically using safe methods
        matches = []
        query = f"""
        MATCH (c:`{node_type}`)-[:`{relationship_type}`]->(t:Topic {{name: $nodeNames}})
        RETURN c
        """
        with self.driver.session() as session:
            result = session.run(query, parameters={'nodeNames': node_names})
            for record in result:
                record = record[0]
                dict = {'name': record.get('name'), 'description': record.get('description')}
                matches.append(dict)
        return matches

    
if __name__ == "__main__":
    finder = Neo4jSession(uri, username, password)
    user_question = "What interships should I apply for?"
    related_topic = finder.find_similar_nodes(user_question)
    print(related_topic)
    print(finder.construct_and_execute_query(related_topic, 'Consideration','IS_CONSIDERATION_FOR'))
    # frame = finder.query_terms(user_question, "Topic")
    #print(frame)
    finder.close()
