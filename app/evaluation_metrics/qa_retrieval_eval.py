from cloud_services import kg_neo4j
from conversation.retrieve_docs import SearchRetriever
from settings.settings import Settings
settings = Settings()
import logging, os
import pandas as pd
logger = logging.getLogger(__name__)
uri = settings.N4J_URI
username = settings.N4J_USERNAME
password = settings.N4J_PASSWORD
from cloud_services.llm_services import AzureLLMClients, get_llm_client, OpenAIClients
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

import nltk
from wordsegment import load, segment
from nltk.corpus import words

# Load the word corpus
load()
word_list = set(words.words())

class RetrievalEval():
    def __init__(self):
        self.score_list = []
        self.results = []
        self.azure_llm : AzureLLMClients = get_llm_client(api_type='azure',
                        api_version=settings.OPENAI_API_VERSION,
                        endpoint=settings.AZURE_OPENAI_ENDPOINT,
                        model=settings.GPT4_MODEL_NAME,
                        deployment=settings.GPT4_DEPLOYMENT_NAME,
                        embedding_deployment=settings.EMBEDDING)
        self.openai_llm : OpenAIClients = get_llm_client(api_type='openai',
                model=settings.OPENAI_DIRECT_MODEL,
              api_key=settings.OPENAI_API_KEY)
        self.retriever = SearchRetriever.with_default_settings()
        self.retriever_catalog = SearchRetriever.with_default_settings(index_name=settings.SEARCH_INDEX_NAME)

    def split_words(self, s):
        # Try to segment using wordsegment library
        segmented = segment(s)
        # Check if the segmented words are in the dictionary
        if all(word in word_list for word in segmented):
            concat_str = ' '.join(segmented)
            if isinstance(concat_str, str):
                return concat_str
            if isinstance(concat_str, tuple):
                return concat_str[0]
        if isinstance(s, str):
            return s
        if isinstance(s, tuple):
            return s[0]
        return s,  # If no valid split is found, return the original string

    def hypothetical_document(self, text):
        from cloud_services.openai_response_objects import Message, ChatCompletion
        def message(role, text):
            return Message(role=role, content=text)
        prompt_template = f'''
        You are a creating university web pages for a fictional university. You are tasked with creating a that would appear on a typical university website, that might address the question below.
        Make sure that the page makes sense in the context of a university website, in which the answer to the question might just be one part of the page.  For example, if the question is about meal plans, create a hypothetical page about campus dining services.  
        If the page is about semester start and end dates, make a hypothetical page about the academic calendar, and so on. 
        Your response should be formatted in markdown and represent the text content of the page.  You can invent fake information as needed to make the page look realistic.
        '''
        message_list = [message('assistant', prompt_template),message('user', text)]
        result : ChatCompletion = self.openai_llm.chat(message_list, False)
        return result.choices[0].message.content

    def embed(self, text):
        return self.azure_llm.embed_to_array(text)
    
    def validate_input(self, data_dict: dict, column_list: list[str]):
        for column in column_list:
            if column in data_dict.keys():
                continue
            else:
                logger.error(f"column missing in input: {column}")
                raise Exception(f"column missing in input: {column}")
        return True
    
    def read_csv(self, filepath: str): 
        return pd.read_csv(filepath)
    
    def get_results(self, input, n=30, type = 'vector'):
        results = []
        if type == 'vector':
            results = self.retriever.retrieve_content(input, n)
        elif type == 'keyword':
            results = self.retriever.retrieve_keyword_content(input, n)
        elif type == 'hybrid':
            results = self.retriever.retrieve_content(input, n)
            results1 = self.retriever.retrieve_keyword_content(input, 2)
            for key in results:
                if key in results1:
                    results[key].extend(results1[key])

        try: 
            self.validate_input(results, ['source', '@search.score', 'page_content', 'days_since_modified', 'subdomain', 
                                                'first_path_item', 'second_path_item', 'sentence_count', 'link_depth' ])
        except Exception as e:
            raise e

        i = 0
        for result in results.get('source'):
            self.results.append({'input': input,
                                'source': result,
                                'score': results.get('@search.score')[i],
                                'content': results.get('page_content')[i],
                                'days_since_modified': results.get('days_since_modified')[i],
                                'subdomain': results.get('subdomain')[i],
                                'first_path_item': results.get('first_path_item')[i],
                                'second_path_item': results.get('second_path_item')[i],
                                'sentence_count': results.get('sentence_count')[i],
                                'link_depth': results.get('link_depth')[i],})
            i += 1

    def group_results(self, n=3):
        if self.results.empty:
            return
        else:
            if 'input' in self.results.columns:
                self.results = self.results.groupby('input').apply(lambda x: x.nlargest(n, 'rescore'))
            else:
                return

    def process_search(self, df: pd.DataFrame, text_col: str, n: int = 30):
        df_dict = df.to_dict(orient='records')
        for topic in df_dict:
            if topic.get('message_role') == 'system' or topic.get('message_role') == 'assistant':
                continue
            if topic.get(text_col, None) == None: 
                logger.error("text not found in input")
                raise Exception("text not found in input")
            else:
                self.get_results(topic.get(text_col), n)
        return
    
    def results_to_string(self):
        rag_str = ''
        if not self.results.empty():
            self.group_results()
            rag_dict = self.results.to_dict(orient='records')
            for item in rag_dict:
                rag_str += f'url: {item.get("source")}, content: {item.get('content')}\n'
        return rag_str
    
    def calculate_columns(self):
        df = pd.DataFrame(self.results)
        df = df[df['days_since_modified'] < 730]
        #df = df[df['sentence_count'] > 3]
        df = df[df['score'] > 0.61]
        if df.empty:
            return df
        df['subdomain_similarity'] = df.apply(lambda x: self.keyword_match(x['subdomain'], x['input']), axis=1)
        df['first_path_similarity'] = df.apply(lambda x: self.keyword_match(x['first_path_item'], x['input']), axis=1)
        df['second_path_similarity'] = df.apply(lambda x: self.keyword_match(x['second_path_item'], x['input']), axis=1)

        scaler = MinMaxScaler()
        columns_to_normalize = ['first_path_similarity', 'second_path_similarity', 'subdomain_similarity', 'score']
        scaled_column_names = [f'scaled_{col}' for col in columns_to_normalize]
        df[scaled_column_names] = scaler.fit_transform(df[columns_to_normalize])
        df_dict = df.to_dict(orient='records')

        df['rescore'] = df.apply(lambda x: self.rescore(x['score'],
                                                        x['scaled_subdomain_similarity'],
                                                        x['subdomain_similarity'],
                                                        x['scaled_first_path_similarity'],
                                                        x['first_path_similarity'],
                                                        x['scaled_second_path_similarity'],
                                                        x['second_path_similarity'],
                                                        x['input'],
                                                        x['link_depth']), axis=1)
        df = df[df['rescore'] > 0.61]
        self.results = df
        return
        
    def results_to_csv(self, path: str):
        return self.results.to_csv(path, index=False)

    def keyword_match(self, text, keywords):
        if not text or text == 'nan' or keywords == 'nan':
            return 0
        
        if text == 'www' or text== '':
            return 0

        text = text.replace('-', ' ').replace('_', ' ')

        if not len(text.split(' ')) > 1:
            text = self.split_words(text)
        
        for item in self.score_list:
            if item.get('text') == text and item.get('keywords') == keywords:
                return item.get('score')
            
        print(f"evaluating similarity between {text} and {keywords}")
        
        if isinstance(text, str):   
            text_embedding = self.embed(text)
        else:
            return 0
        if isinstance(keywords, str):
            keyword_embedding = self.embed(keywords)
            sim_score = {"sim_score": cosine_similarity([keyword_embedding], [text_embedding])[0][0]}
        self.score_list.append({'text': text, 'keywords': keywords, 'score': sim_score.get('sim_score')})
        return sim_score.get('sim_score')

    
    def rescore(self, score, scaled_subdomain_similarity, subdomain_similarity, scaled_first_path_similarity, first_path_similarity, scaled_second_path_similarity, second_path_similarity, text, link_depth):
        path_complexity_adjustment = .3
        subdomain_complexity_adjustment = .6
        scale_adjust = .25

        subdomain_adjusted = 0
        first_path_adjusted = 0
        second_path_adjusted = 0

        if len(text.split(' ')) > 10 and link_depth > 1:
            path_complexity_adjustment = .6

        if isinstance(subdomain_similarity, float):
            if subdomain_similarity > 0:
                subdomain_adjusted = (subdomain_similarity-scale_adjust) * (subdomain_complexity_adjustment)
            if isinstance(first_path_similarity, float):
                if first_path_similarity > 0:
                    first_path_adjusted = (first_path_similarity-scale_adjust) * (path_complexity_adjustment)
                if isinstance(second_path_similarity, float) and second_path_similarity > 0:
                    if second_path_similarity > 0:
                        second_path_adjusted = (second_path_similarity-scale_adjust) * (.5*path_complexity_adjustment)
                    return subdomain_adjusted + first_path_adjusted + second_path_adjusted + score
                return subdomain_adjusted + first_path_adjusted + score
            return subdomain_adjusted + score
        return score

        

# Apply embedding to each row
#df['description_embedding'] = df['description'].apply(embed_text)
#df['content_embedding'] = df['content'].apply(embed_text)


if __name__ == '__main__':
    gc = kg_neo4j.Neo4jSession(uri, username, password)
    
    eval = RetrievalEval()
    df = pd.read_csv('exported_messages.csv')
    #limit for testing
    df = df.iloc[:50]
    score_set = []
    #topics = [{'name': 'What types of events are there at Tech for current students?', 'description': 'What types of events are there at Tech for current students?'}
     #         ,{'name': 'What kind of mental health supports are available for online students?', 'description': 'What kind of mental health supports are available for online students?'}
    #          ,{'name': 'what is the cafeteria like on campus? Is the food good?', 'description': 'what is the cafeteria like on campus? Is the food good?'}]
    
    df = eval.process_search(df, 'message_content', 20)
    eval.results_to_csv('intermediate_results.csv')

    # Find the source link corresponding to the max score
    max_score_indices = eval.group_results(df)

    print(max_score_indices.head())
    max_score_indices.to_csv('max_score_indices.csv', index=False)



# Compare this snippet from app/evaluation_metrics/nlp.py: