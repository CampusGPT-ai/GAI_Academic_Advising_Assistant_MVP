import pandas as pd 
from data.models import WebPageDocumentNew
from settings.settings import Settings
df1 = pd.read_csv('/Users/marynelson/GAI_Academic_Advising_Assistant_MVP/app/evaluation_metrics/itech_processed.csv')
import math 
from time import sleep
settings = Settings()
from mongoengine import connect, disconnect
import mongoengine.connection


db_name = settings.MONGO_DB
db_conn = settings.MONGO_CONN_STR

_mongo_conn = connect(db=db_name, host=db_conn)

while True and WebPageDocumentNew.objects().count() > 0:
    try:
        WebPageDocumentNew.objects().delete()
    except:
        sleep(1)

results = 0
print(df1.shape)
# Select specific columns
selected_columns = df1[['metadata/canonicalUrl',
                         'metadata/jsonLd/0/@graph/0/dateModified',
                         'metadata/jsonLd/0/@graph/0/description',
                         'metadata/keywords',
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
result_dict = selected_columns.to_dict(orient='records')

docs_list = []

def safe_get(dictionary, key):
    value = dictionary.get(key, "")
    return value if not (isinstance(value, float) and math.isnan(value)) else ""


for result in result_dict:
    try:
        doc = WebPageDocumentNew(
                source=safe_get(result, 'metadata/canonicalUrl'),
                last_modified=safe_get(result, 'metadata/jsonLd/0/@graph/0/dateModified'),
                metadata_description=safe_get(result, 'metadata/jsonLd/0/@graph/0/description'),
                metadata_keywords=safe_get(result, 'metadata/keywords'),
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
        doc.save()
        results += 1
        print(f"Saved {results} documents")
        docs_list.append(doc)
    except Exception as e:
        print(f"Error saving document: {e}, skipping...")
        continue

print('done')