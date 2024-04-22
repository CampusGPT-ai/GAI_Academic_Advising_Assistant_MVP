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