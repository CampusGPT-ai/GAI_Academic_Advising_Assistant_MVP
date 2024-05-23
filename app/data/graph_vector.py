from cloud_services.llm_services import AzureLLMClients, get_llm_client
from settings.settings import Settings
from cloud_services.kg_neo4j import Neo4jSession
settings = Settings()


azure_llm_client : AzureLLMClients = get_llm_client(api_type='azure',
                                                    api_version=settings.OPENAI_API_VERSION,
                                                    endpoint=settings.AZURE_OPENAI_ENDPOINT,
                                                    model=settings.GPT35_MODEL_NAME,
                                                    deployment=settings.GPT35_DEPLOYMENT_NAME,
                                                    embedding_deployment=settings.EMBEDDING)
class GraphVector:
    def __init__(self):
        self.graph = Neo4jSession(uri=settings.N4J_URI, user=settings.N4J_USERNAME, password=settings.N4J_PASSWORD)

    @staticmethod
    def _embed(text):
        return azure_llm_client.embed_to_array(text)

    def add_vector(self):
        with self.graph.driver.session() as session:
            result = session.run('''
                MATCH (n) 
                WHERE n.description IS NOT NULL 
                RETURN id(n) AS id, n.description AS description''')

            for record in result:
                node_id = record["id"]
                description = record["description"]
                
                # Generate embedding
                embedding = self._embed(description)
                print('adding embedding for node:', node_id)
                
                # Update the node with the embedding (create a new property, e.g., 'embedding')
                session.run('''
                    MATCH (n) WHERE id(n) = $id 
                    SET n.embedding = $embedding'''
                                , id=node_id, embedding=embedding)
    
        self.graph.driver.close()
    
    def add_single_vector(self, name):
        with self.graph.driver.session() as session:
            result = session.run(f'''
                MATCH (n) 
                WHERE n.name = $name
                RETURN id(n) AS id, n.description AS description''', {'name': name})

            for record in result:
                node_id = record["id"]
                description = record["description"]
                
                # Generate embedding
                embedding = self._embed(description)
                
                # Update the node with the embedding (create a new property, e.g., 'embedding')
                session.run('''
                    MATCH (n) WHERE id(n) = $id 
                    SET n.embedding = $embedding'''
                                , id=node_id, embedding=embedding)
    
        self.graph.driver.close()


if __name__ == "__main__":
    graph = GraphVector()
    graph.add_vector()
    print("Graph vector added")