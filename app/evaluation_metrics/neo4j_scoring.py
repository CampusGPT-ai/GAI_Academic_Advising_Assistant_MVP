import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from neo4j import GraphDatabase
from cloud_services.llm_services import AzureLLMClients, get_llm_client
from settings.settings import Settings

# Load settings for Neo4j and Azure LLM
settings = Settings()
uri = settings.N4J_URI
username = settings.N4J_USERNAME
password = settings.N4J_PASSWORD

azure_llm_client: AzureLLMClients = get_llm_client(api_type='azure',
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

    def add_content_node(self, source, content):
        with self.driver.session() as session:
            session.run("""
                CREATE (n:Content {source: $source, content: $content})
            """, source=source, content=content)

    def add_vector(self):
        with self.driver.session() as session:
            result = session.run('''
                MATCH (n:Content) 
                WHERE n.content IS NOT NULL 
                RETURN id(n) AS id, n.content AS content''')

            for record in result:
                node_id = record["id"]
                content = record["content"]
                
                # Generate embedding
                embedding = azure_llm_client.embed_to_array(content)
                
                # Update the node with the embedding (create a new property, e.g., 'embedding')
                session.run('''
                    MATCH (n) WHERE id(n) = $id 
                    SET n.embedding = $embedding''', id=node_id, embedding=embedding)
    
    def find_similar_nodes_with_score(self, text, top_k=3):
            query_vector = azure_llm_client.embed_to_array(text)

            with self.driver.session() as session:
                result = session.run("""
                    CALL db.index.vector.queryNodes('contentIndex', 3, $queryVector)
                    YIELD node AS similarNode, score
                    RETURN similarNode.source AS source, similarNode.content AS content, score
                    ORDER BY score DESC
                """, parameters={'queryVector': query_vector})

                # Collect all records into a list
                similar_nodes = []
                for record in result:
                    similar_nodes.append({
                        'source': record['source'],
                        'content': record['content'],
                        'score': record['score']
                    })

                return similar_nodes


def main():
    # Load the CSV file
    file_path = 'aggregated_results.csv'
    df = pd.read_csv(file_path)

    # Check if the necessary columns are present
    if 'source' not in df.columns or 'content' not in df.columns or 'description' not in df.columns:
        raise ValueError("The CSV file must contain 'source', 'content', and 'description' columns.")

    # Fill NaN values with empty strings to avoid issues with vectorization
    df['source'] = df['source'].fillna('')
    df['content'] = df['content'].fillna('')
    df['description'] = df['description'].fillna('')

    # Initialize Neo4j session
    neo4j_session = Neo4jSession(uri, username, password)

    # Add nodes to Neo4j
    #for _, row in df.iterrows():
        #neo4j_session.add_content_node(row['source'], row['content'])

    # Add embeddings to nodes
    #neo4j_session.add_vector()

    # Iterate through the descriptions and get similarity scores
    similarity_scores = []
    for description in df['description']:
        similar_nodes = neo4j_session.find_similar_nodes_with_score(description)
        if similar_nodes:
            # Use the highest score from the similar nodes
            highest_score = similar_nodes[0]['score']
        else:
            highest_score = 0
        similarity_scores.append(highest_score)

    # Append the similarity scores to the dataframe
    df['neo4j_cosine_similarity'] = similarity_scores

    # Save the updated dataframe back to the CSV file
    df.to_csv(file_path, index=False)

    neo4j_session.close()

if __name__ == "__main__":
    main()
