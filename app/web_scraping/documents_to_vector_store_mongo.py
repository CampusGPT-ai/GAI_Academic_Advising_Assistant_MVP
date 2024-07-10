import uuid
import os, time
from dotenv import load_dotenv
import web_scraping.llm_services as llm
from web_scraping.azure_cog_service import AzureSearchService
from datetime import datetime
import pytz

from settings.settings import Settings
settings = Settings()
from mongoengine import connect, disconnect

from data.models import WebPageDocumentNew, indexDocumentv2

db_name = settings.MONGO_DB
db_conn = settings.MONGO_CONN_STR
_mongo_conn = connect(db=db_name, host=db_conn)
load_dotenv()

#change indexes as needed

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_VERSION = os.getenv("OPENAI_API_VERSION")
OPENAI_ENDPOINT= os.getenv("AZURE_ENDPOINT")
OPENAI_DEPLOYMENT = os.getenv("DEPLOYMENT_NAME")
OPENAI_MODEL = os.getenv("MODEL_NAME")
EMBEDDING = os.getenv("EMBEDDING")
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_API_KEY= os.getenv("SEARCH_API_KEY")
SEARCH_INDEX_NAME=os.getenv("SEARCH_INDEX_NAME")
EMBEDDING_DEPLOYMENT = os.getenv("EMBEDDING")
MAX_TOKEN_LENGTH = 6000
BATCH_SIZE = 100


#while True and indexDocumentv2.objects().count() > 0:
#    try:
 #       indexDocumentv2.objects().delete()
#    except:
 #       sleep(1)

class VectorUploader():
    def __init__(self):
        self.azure_llm = llm.get_llm_client(api_type='azure',
                                api_version=OPENAI_VERSION,
                                endpoint=OPENAI_ENDPOINT,
                                model=OPENAI_MODEL,
                                deployment=OPENAI_DEPLOYMENT,
                                embedding_deployment=EMBEDDING_DEPLOYMENT)
        
        self.search_client = AzureSearchService(SEARCH_ENDPOINT,
                                                SEARCH_INDEX_NAME,
                                                self.azure_llm,
                                                SEARCH_API_KEY)

    def refresh_client(self):
        self.azure_llm = llm.get_llm_client(api_type='azure',
                                api_version=OPENAI_VERSION,
                                endpoint=OPENAI_ENDPOINT,
                                model=OPENAI_MODEL,
                                deployment=OPENAI_DEPLOYMENT,
                                embedding_deployment=EMBEDDING_DEPLOYMENT)
        
        self.search_client = AzureSearchService(SEARCH_ENDPOINT,
                                                SEARCH_INDEX_NAME,
                                                self.azure_llm,
                                                SEARCH_API_KEY)
        
    def check_upload_status(self):
        documents_already_processed = set()
        for doc in indexDocumentv2.objects():  # Query all documents
            documents_already_processed.add(doc.page_content)
        return documents_already_processed
    
    def trim_upload_list(self):
        return_docs = []
        indexed_docx = self.check_upload_status()
        doc_list = WebPageDocumentNew.objects().all()
        for doc in doc_list:
            if doc.page_content not in indexed_docx:
                return_docs.append(doc)
        return return_docs

    def upload_files(self, reupload=False):
        uploaded = 0
        retry_delay = 10
        docs_to_upload = []
        processed_docs = []
        batch_size = BATCH_SIZE
        if not reupload: 
            doc_list = self.trim_upload_list()
            print("Documents to index: ", len(doc_list))
        else:
            indexed_docs = set()
            doc_list = indexDocumentv2.objects()
        try:
            for doc in doc_list:
                try:
                    try:
                        doc_processed = self.json_to_index(doc, reupload)
                    except:
                        continue
                    # when batch is greater than 100, upload to azure search and save to mongo.
                    if len(docs_to_upload) >= batch_size or (len(doc_list)-uploaded)<=batch_size:
                        results = self.search_client.upload(docs_to_upload)
                        is_error = False
                        for result in results:
                            if not result.succeeded:
                                print(f"Failed to upload document: {result.key}")
                                is_error = True
                        if not is_error: 
                            print(f"Document uploaded successfully: {len(docs_to_upload)}")
                            uploaded += len(docs_to_upload)
                            print(f"Total documents uploaded: {uploaded}")
                        
                        # save processed documents to mongo db (faster if need to re-upload)
                        if not reupload:
                            processed_docs = self.index_to_doc(docs_to_upload)
                            if processed_docs:
                                for doc in processed_docs:
                                    doc.save()
                                print("Documents saved to mongo: ", len(processed_docs))

                        # reset batches for next iteration
                        processed_docs = [] 
                        docs_to_upload = []
                    else:
                        docs_to_upload.append(doc_processed)

                except Exception as e:
                    if "Unauthorized" in str(e):
                        self.refresh_client()
                    if "rate limit" in str(e).lower() or "429" in str(e):
                        print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        print(f"exception logged for {str(e)}") 
                finally:
                    next
        except Exception as e:
            print(f"exception logged for {str(e)}")
        finally:
            disconnect()
    
    # convert list of json strings to mongo documents
    def index_to_doc(self, json_data):
        output = []

        for item in json_data:
            dict_item = indexDocumentv2(
                vector_id=item.get("vector_id", ""),
                source=item.get("source", ""),
                content_vector=item.get("content_vector", None),
                last_modified=item.get("last_modified", ""),
                metadata_description=item.get("metadata_description", ""),
                metadata_keywords=item.get("metadata_keywords", ""),
                page_content=item.get("page_content", ""),
                days_since_modified=item.get("days_since_modified", ""),
                word_count=item.get("word_count", 0),
                sentence_count=item.get("sentence_count", 0),
                char_count=item.get("char_count", 0),
                average_word_length=item.get("average_word_length", 0),
                average_sentence_length=item.get("average_sentence_length", 0),
                header_count=item.get("header_count", 0),
                list_count=item.get("list_count", 0),
                link_count=item.get("link_count", 0),
                subdomain=item.get("subdomain", ""),
                first_path_item=item.get("first_path_item", ""),
                second_path_item=item.get("second_path_item", ""),
                link_depth=item.get("link_depth", 0),
                link_depth_class=item.get("link_depth_class", 0),
                age_class=item.get("age_class", 0),
                sentence_count_class=item.get("sentence_count_class", 0)
            )

            output.append(dict_item)

        return output
                        
        
    def embed(self, text):
        try:
            result = self.azure_llm.embed_to_array(text)
        except Exception as e:
            if "rate limit" in str(e).lower() or "429" in str(e):
                print(f"Rate limit exceeded. Retrying in 20 seconds...")
                time.sleep(20)
            else: 
                raise e
        return result
    


    def convert_to_edm_datetimeoffset(self, date_string):
        dt = datetime.fromisoformat(date_string)
        dt = dt.replace(tzinfo=pytz.UTC)
        edm_datetimeoffset = dt.isoformat()
        return edm_datetimeoffset
        
    
    def json_to_index(self, document, reupload):
        
        try:
            if reupload: 
                index_document = {
                    "@search.action": "upload",
                    "source": document.source,
                    "content_vector": document.content_vector,
                    "last_modified": document.last_modified,
                    "metadata_description": document.metadata_description,
                    "metadata_keywords": document.metadata_keywords,
                    "page_content": document.page_content,
                    "days_since_modified": document.days_since_modified,
                    "word_count": document.word_count,
                    "sentence_count": document.sentence_count,
                    "char_count": document.char_count,
                    "average_word_length": document.average_word_length,
                    "average_sentence_length": document.average_sentence_length,
                    "header_count": document.header_count,
                    "list_count": document.list_count,
                    "link_count": document.link_count,
                    "subdomain": document.subdomain,
                    "first_path_item": document.first_path_item,
                    "second_path_item": document.second_path_item,
                    "link_depth": document.link_depth,
                    "link_depth_class": document.link_depth_class,
                    "age_class": document.age_class,
                    "sentence_count_class": document.sentence_count_class
                }
            else: 
                index_document = {
                    "@search.action": "upload",
                    "vector_id": str(uuid.uuid4()),
                    "source": document.source,
                    "content_vector": self.embed(document.page_content),
                    "last_modified": self.convert_to_edm_datetimeoffset(document.last_modified),
                    "metadata_description": document.metadata_description,
                    "metadata_keywords": document.metadata_keywords,
                    "page_content": document.page_content,
                    "days_since_modified": document.days_since_modified,
                    "word_count": document.word_count,
                    "sentence_count": document.sentence_count,
                    "char_count": document.char_count,
                    "average_word_length": document.average_word_length,
                    "average_sentence_length": document.average_sentence_length,
                    "header_count": document.header_count,
                    "list_count": document.list_count,
                    "link_count": document.link_count,
                    "subdomain": document.subdomain,
                    "first_path_item": document.first_path_item,
                    "second_path_item": document.second_path_item,
                    "link_depth": document.link_depth,
                    "link_depth_class": document.link_depth_class,
                    "age_class": document.age_class,
                    "sentence_count_class": document.sentence_count_class,
                    "subdomain_vector": self.embed(document.subdomain),
                    "first_path_vector": self.embed(document.first_path_item),
                    "second_path_vector": self.embed(document.second_path_item)
                }
        except Exception as e: 
            print(f"exception logged for {str(e)} with document {document.source}")
            raise Exception("unable to parse json document due to malformed text")
        
        return index_document
    
if __name__ == "__main__":
    loader = VectorUploader()
    loader.upload_files(reupload=False)
    print("Upload complete")

            


