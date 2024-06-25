from conversation.prompt_templates.classify_graph_prompt import get_gpt_classification_prompt
import json, os
from data.models import ConversationSimple as Conversation, UserSession
from conversation.run_chat import QueryLLM
import logging
from cloud_services.openai_response_objects import Message
from cloud_services.connect_mongo import MongoConnection
from queue import Queue
logger = logging.getLogger(__name__)
from user.get_user_info import UserInfo
import asyncio

# input user question - update considerations in profile.  No yield, asynch call
class Considerations:
    def __init__(self, user_session, question):
        self.user_question = question
        self.user_session = user_session
        self.user_id = user_session.user_id
        self.user = UserInfo(self.user_id)
        self.user_considerations = self._set_user_considerations()

    def _set_user_considerations(self):
        if self.user:
            user_info = self.user.get_user_info()
            if isinstance(user_info, str):
                considerations = ""
            else:
                considerations = user_info.considerations
            return considerations
        else: 
            return []

    def get_consideration_keys(self):
        keys = []
        for consideration in self.user_considerations:
            key = consideration.keys()
            keys.extend(list(key))
        return keys

    def get_consideration_descriptions(self, name):
        descriptions = []
        for consideration in self.user_considerations:
            if consideration.keys() == name:
                descriptions.append(consideration.values())
        return descriptions
    
    ## adding consideration matches to output
    def match_profile_to_graph(self, graph_considerations):
        profile_considerations = self.get_consideration_keys()
        missing_considerations = []
        matching_considerations = []
        for consideration in graph_considerations:
            if consideration.get('name') not in profile_considerations:
                missing_considerations.append(consideration)
            else:
                matching_considerations.append(consideration)
        return missing_considerations, matching_considerations

    def match_llm_to_profile(self, new_considerations):

        missing_considerations = self.user_considerations
        consideration_dictionary = {}
        if new_considerations.get('considerations'):
            for consideration in new_considerations.get('considerations'):
                missing_considerations.append({consideration.get('name'): consideration.get('user information')})

        list_tuples = {tuple(d.items())[0] for d in missing_considerations}

        for (n,d) in list_tuples:
            if n not in consideration_dictionary:
                consideration_dictionary[n] = d
            else:
                consideration_dictionary[n] = d + ", " + consideration_dictionary[n]

        missing_considerations = [{k: v} for k, v in consideration_dictionary.items()]

        return missing_considerations
        

    def update_considerations(self, new_considerations, conversation):
        missing_considerations = self.match_llm_to_profile(new_considerations)

        try:
            self.user.user_profile.considerations = missing_considerations
            self.user.user_profile.active_conversation = conversation
            self.user.user_profile.save()
            return True
        except Exception as e:
            logger.error(f"Error saving considerations: {e}")
            return e
    
    def check_considerations(self, history: list[Message], graph_considerations):
        # first check the users answer to see if any new considerations are revealed
        llm_query = QueryLLM(self.user_session) 
        classification_prompt, classification_json = llm_query.create_prompt_template(
            get_gpt_classification_prompt(graph_considerations, json.dumps(self.user_considerations)),history=history, user_question=self.user_question)
        response = llm_query.run_llm(classification_prompt, classification_json)
        return response
    
    def run_all(self, history, all_considerations, conversation):
        graph_considerations, _ = self.match_profile_to_graph(all_considerations)
        new_considerations = self.check_considerations(history, graph_considerations)
        if new_considerations.get('contains considerations')=='no':
            return
        self.update_considerations(new_considerations, conversation)

    async def run_all_async(self, history, all_considerations, conversation):
        return await asyncio.to_thread(self.run_all, history, all_considerations, conversation)   

    
if __name__=="__main__":
    from pathlib import Path

    from mongoengine import connect
    import os
    from conversation.retrieve_messages import get_history_as_messages

    mongo_conn = MongoConnection()
    mongo_conn.connect()

    USER_QUESTION = "what internships should I pursue.  I am interested in robotics and physics."
    USER_ID = "A_iXG9LQjG86PTY1sgG-Sm9JO3IbMlliRkZok3BhT8I"

    relative_path = Path('./app/data/mock_user_session.json')
    with relative_path.open(mode='r') as file:
        mock_user_session : UserSession = UserSession(**json.load(file))

    mock_conversation = Conversation.objects(id="6622fed0fcda8e6d6c33fb04").select_related(max_depth=5)

    from conversation.run_graph import GraphFinder
    history = get_history_as_messages(mock_conversation[0].id)
    finder = GraphFinder(mock_user_session, USER_QUESTION)
    c = Considerations(mock_user_session, USER_QUESTION)
    topic = finder.get_topic_from_question()
    all_considerations = finder.get_relationships('Consideration',topic)

    asyncio.run(c.run_all_async(history, all_considerations, mock_conversation[0]))

    #mongo_conn.disconnect_all() 




