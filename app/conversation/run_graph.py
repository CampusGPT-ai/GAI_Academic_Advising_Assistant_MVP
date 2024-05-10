from settings.settings import Settings
from cloud_services.kg_neo4j import Neo4jSession
from threading import Thread
settings = Settings()

class GraphFinder:
    def __init__(self, user_session, user_question):
        self.user_question = user_question
        self.user_session = user_session
        self.user_id = user_session.user_id
        self.finder = None

    def get_topic_from_question(self):
        self.init_neo4j()
        return self.finder.find_similar_nodes(self.user_question)
    
    def get_topic_list_from_question(self):
        self.init_neo4j()
        return self.finder.find_similar_nodes_with_score(self.user_question)

    def get_all_considerations(self):
        self.init_neo4j()
        all_considerations = self.finder.find_all_nodes()
        return all_considerations

    def get_relationships(self, type, related_topics):
        self.init_neo4j()
        if type == 'Consideration':
            graph_considerations = self.finder.query_considerations(related_topics, type, 'IS_CONSIDERATION_FOR')
            return graph_considerations
        elif type == 'Outcome':
            risks = self.finder.query_outcomes('IS_RISK_OF',related_topics)
            opportunities = self.finder.query_outcomes('IS_OPPORTUNITY_FOR', related_topics)
            return risks, opportunities

    def init_neo4j(self):
        if self.finder == None:
            self.finder = Neo4jSession(settings.N4J_URI, settings.N4J_USERNAME, settings.N4J_PASSWORD)
        return
    
if __name__ == '__main__':
    from pathlib import Path
    import json, csv
    from data.models import UserSession
    relative_path = Path('./app/data/sample_questions.json')

    with relative_path.open(mode='r') as file:
        mock_questions = json.load(file)

    session_path = Path('./app/data/mock_user_session.json')
    with session_path.open(mode='r') as file:
        mock_user_session : UserSession = UserSession(**json.load(file))
    
    question_list = mock_questions.get('questions')
    results = []

    for question in question_list:
        graph_finder = GraphFinder(mock_user_session, question)
        topic_scores = graph_finder.get_topic_list_from_question()
        for topic_score in topic_scores:
            results.append([question, topic_score['name'], topic_score['score']])

        # Define the CSV file path
        csv_path = Path('questions_topics_scores.csv')

        # Write results to a CSV file
        with csv_path.open(mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Question', 'Topic', 'Score'])  # Writing headers
            writer.writerows(results)

        print(f"Data written to {csv_path.absolute()}")


