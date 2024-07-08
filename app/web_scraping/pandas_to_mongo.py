import pandas as pd 
from data.models import WebPageDocumentNew
from settings.settings import Settings
import math 
from time import sleep
settings = Settings()
from mongoengine import connect
import time


db_name = settings.MONGO_DB
db_conn = settings.MONGO_CONN_STR

_mongo_conn = connect(db=db_name, host=db_conn)

#while True and WebPageDocumentNew.objects().count() > 0:
 #   print(WebPageDocumentNew.objects().count())
 #   try:
 #       WebPageDocumentNew.objects().delete()
 #   except:
  #      sleep(1)
 
def read_df(df):
    print(df.shape)
    # Select specific columns
    selected_columns = df[['canonicalUrl',
                            'dateModified',
                            'description',
                            'title',
                            'markdown',
                            'days_since_modified',
                            'word_count',
                            'sentence_count',
                            'char_count',
                            'average_word_length',
                            'average_sentence_length',
                            'header_count',
                            'list_count',
                            'link_count',
                            'subdomain',
                            'first_path_item',
                            'second_path_item',
                            'link_depth',
                            'link_depth_class',
                            'age_class',
                            'sentence_count_class'
                            ]]

    # Convert the selected columns to a dictionary
    return selected_columns.to_dict(orient='records')

def safe_get(dictionary, key):
    value = dictionary.get(key, "")
    return value if not (isinstance(value, float) and math.isnan(value)) else ""


def add_docs(result_dict, batch_size=50):
    total_docs = len(result_dict)
    for i in range(0, total_docs, batch_size):
        batch = result_dict[i:i + batch_size]
        docs = []
        for result in batch:
            try:
                doc = WebPageDocumentNew(
                    source=safe_get(result, 'canonicalUrl'),
                    last_modified=safe_get(result, 'dateModified'),
                    metadata_description=safe_get(result, 'description'),
                    metadata_keywords=safe_get(result, 'title'),
                    page_content=safe_get(result, 'markdown'),
                    days_since_modified=safe_get(result, 'days_since_modified'),
                    word_count=safe_get(result, 'word_count'),
                    sentence_count=safe_get(result, 'sentence_count'),
                    char_count=safe_get(result, 'char_count'),
                    average_word_length=safe_get(result, 'average_word_length'),
                    average_sentence_length=safe_get(result, 'average_sentence_length'),
                    header_count=safe_get(result, 'header_count'),
                    list_count=safe_get(result, 'list_count'),
                    link_count=safe_get(result, 'link_count'),
                    subdomain=safe_get(result, 'subdomain'),
                    first_path_item=safe_get(result, 'first_path_item'),
                    second_path_item=safe_get(result, 'second_path_item'),
                    link_depth=safe_get(result, 'link_depth'),
                    link_depth_class=safe_get(result, 'link_depth_class'),
                    age_class=safe_get(result, 'age_class'),
                    sentence_count_class=safe_get(result, 'sentence_count_class')
                )
                docs.append(doc)
            except Exception as e:
                print(f"Error preparing document: {e}, skipping...")
                continue

        while True:
            try:
                if docs:
                    WebPageDocumentNew.objects.insert(docs, load_bulk=False)
                    print(f"Saved batch of {len(docs)} documents")
                break
            except Exception as e:
                print(f"Error saving batch: {e}. Retrying in 30 seconds...")
                time.sleep(30)

    print('done')
    return

if __name__=="__main__":

    from web_scraping.apify_page_count import process_results, run_all
    results = run_all('international.ucf.edu', ['events', 'news', 'publication'])
    df1 = process_results(results)
    result_dict = read_df(df1)
    add_docs(result_dict)
