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
from cloud_services.llm_services import AzureLLMClients, get_llm_client
from sklearn.metrics.pairwise import cosine_similarity

import nltk
from wordsegment import load, segment
from nltk.corpus import words

# Load the word corpus
load()
word_list = set(words.words())

class RetrievalEval():
    def __init__(self):
        self.score_list = []
        self.azure_llm : AzureLLMClients = get_llm_client(api_type='azure',
                        api_version=settings.OPENAI_API_VERSION,
                        endpoint=settings.AZURE_OPENAI_ENDPOINT,
                        model=settings.GPT4_MODEL_NAME,
                        deployment=settings.GPT4_DEPLOYMENT_NAME,
                        embedding_deployment=settings.EMBEDDING)


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



    def embed(self, text):
        return self.azure_llm.embed_to_array(text)

    def keyword_match(self, text, keywords, topic=None, source=None):
        if not text:
            return 0, 0

        text = text.replace('-', ' ').replace('_', ' ')

        if not len(text.split(' ')) > 1:
            text = self.split_words(text)
        
        for item in self.score_list:
            if item.get('text') == text and item.get('keywords') == keywords:
                return item.get('score')
            
        print(f"evaluating similarity between {text} and {keywords}")
        sims = pd.DataFrame()
        
        
        if isinstance(text, str):   
            text_embedding = self.embed(text)
        else:
            return 0, 0
        for keyword in keywords.split(','):
            if isinstance(keyword, str):
                keyword_embedding = self.embed(keyword)
            else:
                next
            sim_score = {"sim_score": cosine_similarity([keyword_embedding], [text_embedding])[0][0]}
            sim_score_df = pd.DataFrame([sim_score])
            sims = pd.concat([sims, sim_score_df], ignore_index=True)  # Concatenate DataFrames

        max_score = sims['sim_score'].max()
        self.score_list.append({'text': text, 'keywords': keywords, 'score': max_score})
        return max_score
    
    def rescore(self, score, subdomain_similarity, first_path_similarity, second_path_similarity):
        if isinstance(subdomain_similarity, float) and subdomain_similarity > 0:
            subdomain_adjusted = (subdomain_similarity-.4) * .6
            if isinstance(first_path_similarity, float) and first_path_similarity > 0:
                first_path_adjusted = (first_path_similarity-.4) * .3
                if isinstance(second_path_similarity, float) and second_path_similarity > 0:
                    second_path_adjusted = (second_path_similarity-.4) * .1
                    return subdomain_adjusted + first_path_adjusted + second_path_adjusted + score
                return subdomain_adjusted + first_path_adjusted + score
            return subdomain_adjusted + score
        return score

        

# Apply embedding to each row
#df['description_embedding'] = df['description'].apply(embed_text)
#df['content_embedding'] = df['content'].apply(embed_text)


if __name__ == '__main__':
    gc = kg_neo4j.Neo4jSession(uri, username, password)
    topics = gc.find_all_nodes('Topic','dict')
    eval = RetrievalEval()

    score_set = []
    #topics = [{'name': 'What types of events are there at Tech for current students?', 'description': 'What types of events are there at Tech for current students?'}
     #         ,{'name': 'What kind of mental health supports are available for online students?', 'description': 'What kind of mental health supports are available for online students?'}
    #          ,{'name': 'what is the cafeteria like on campus? Is the food good?', 'description': 'what is the cafeteria like on campus? Is the food good?'}]
    retriever = SearchRetriever.with_default_settings()
    retriever_catalog = SearchRetriever.with_default_settings(index_name=settings.SEARCH_INDEX_NAME)
    score_list = []

    for topic in topics[50:51]:
        #if not topic.get('name') == 'Completing the FAFSA Form':
        #    continue
        results = retriever_catalog.retrieve_content(topic.get('description'),30)
        i = 0
        for result in results.get('source'):
            score_list.append({'topic': topic.get('name'), 'description': topic.get('description'), 'keywords': topic.get('keywords'), 'source': result, 'score': results.get('@search.score')[i], 'content': results.get('page_content')[i],
                                'days_since_modified': results.get('days_since_modified')[i],
                                'subdomain': results.get('subdomain')[i],
                                'first_path_item': results.get('first_path_item')[i],
                                'second_path_item': results.get('second_path_item')[i],
                                'sentence_count': results.get('sentence_count')[i],
                                'link_depth': results.get('link_depth')[i],})
            i += 1

    df = pd.DataFrame(score_list)
    df = df[df['days_since_modified'] < 730]
    df = df[df['sentence_count'] > 3]
    df['subdomain_similarity'] = df.apply(lambda x: eval.keyword_match(x['subdomain'], x['keywords']), axis=1)
    df['first_path_similarity'] = df.apply(lambda x: eval.keyword_match(x['first_path_item'], x['keywords']), axis=1)
    df['second_path_similarity'] = df.apply(lambda x: eval.keyword_match(x['second_path_item'], x['keywords']), axis=1)
    df['rescore'] = df.apply(lambda x: eval.rescore(x['score'], x['subdomain_similarity'], x['first_path_similarity'], x['second_path_similarity']), axis=1)
    df.to_csv('intermediate_results.csv', index=False)


    # Find the source link corresponding to the max score
    max_score_indices = df.groupby('topic')['rescore'].apply(lambda x: x.nlargest(3, 'rescore'))

    print(max_score_indices.head())
    max_score_indices.to_csv('max_score_indices.csv', index=False)



# Compare this snippet from app/evaluation_metrics/nlp.py: