
import logging
from settings.settings import Settings
logger = logging.getLogger(__name__)
settings = Settings()
from evaluation_metrics.qa_retrieval_eval import RetrievalEval
from mongoengine import connect
import os
import pandas as pd
from conversation.prompt_templates.gpt_qa_prompt import get_gpt_system_prompt as gpt_qa_prompt_v1
from cloud_services.openai_response_objects import Message, ChatCompletion
def message(role, text):
    return Message(role=role, content=text)

df = pd.read_csv('exported_messages.csv')
df_dict = df.to_dict(orient='records')
print(df.keys())

results_dict = []


db_name = os.getenv("MONGO_DB")
db_conn = os.getenv("MONGO_CONN_STR")
_mongo_conn = connect(db=db_name, host=db_conn)

def dict_item_to_string(input: dict) -> str:
    for key, value in input.items():
        return f'{key}: {value}'

from cloud_services.llm_services import get_llm_client, OpenAIClients
 
openai_llm : OpenAIClients = get_llm_client(api_type='openai',
                model=settings.OPENAI_DIRECT_MODEL,
              api_key=settings.OPENAI_API_KEY)

for topic in df_dict:
    if not topic.get('message_role') == 'user':
        continue


    rag_str = ''
    retreiver = RetrievalEval()
    user_input = topic.get('message_content')
    #user_input = retreiver.hypothetical_document(user_input)
    retreiver.get_results(user_input, 30, 'hybrid')
    retreiver.calculate_columns()
    if not df.empty:
        retreiver.group_results(df, 5)
        rag_dict = retreiver.results.to_dict(orient='records')
        for item in rag_dict:
            rag_str += f'url: {item.get("source")}, content: {item.get('content')}\n'
    else: 
        rag_str = 'No results found'

    prompt, validation = gpt_qa_prompt_v1('',rag_str)

    def message(content, role):
        return Message(role=role, content=content)

    input = [message(prompt, 'assistant'), message(topic.get('message_content'), 'user')]

    try:
        response: ChatCompletion = openai_llm.chat(input, True)
        response = openai_llm.validate_json(response.choices[0].message.content, validation)
        print(response)
    except Exception as e:
        print(Exception())
        continue
    
    results_dict.append({'user_message': topic.get('message_content'), '' 'assistant_response': response.get('response'), 'context': rag_str})

df = pd.DataFrame(results_dict)
df.to_csv('exported_messages_scoring.csv', index=False)