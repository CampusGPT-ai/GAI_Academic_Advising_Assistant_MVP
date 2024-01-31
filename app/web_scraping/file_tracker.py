import os
import json
import asyncio
from datetime import datetime, timedelta
from queue import Queue  # Import regular Queue
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import BlobSasPermissions, generate_blob_sas, BlobClient
from dotenv import load_dotenv
from azure.core.async_paging import AsyncItemPaged
from threading import Lock, Thread
load_dotenv()

AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
AZURE_STORAGE_ACCOUNT_CRED = os.getenv("AZURE_STORAGE_ACCOUNT_CRED")
AZURE_STORAGE_CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER")
SAS_TOKEN=os.getenv("SAS_TOKEN")
account_url = f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net"

# Define the expiry time for the SAS token (e.g., 1 hour from now)
expiry_time = datetime.utcnow() + timedelta(hours=12)

# Define the permissions for the SAS token (e.g., read access)
permissions = BlobSasPermissions(read=True)

class FileLogger():
    def __init__(self, visited_log, rejected_log, credentials, account_url):
        self.credentials = credentials
        self.account_url = account_url

        # Initialize the blob_service_client here
        self.blob_service_client = BlobServiceClient(account_url=self.account_url, credential=self.credentials)

        self.log = visited_log
        self.failure_log = rejected_log
        self.file_list = []
        self.docs = Queue()  # Use a regular Queue
        self.visited = self.read_logs()
        self.rejected = set()
        self.docs_lock = Lock()
        self.threads = []

    def generate_sas_token(self, cname, bname=None):
        # Generate the SAS token
        return generate_blob_sas(
            account_name=self.blob_service_client.account_name,
            container_name=cname,
            blob_name=bname,
            account_key=self.credentials,
            permission=permissions,
            expiry=expiry_time
        )
    

    def get_blob_client(self, container_name, blob_name, sas_token_pass=None):
        if sas_token_pass == None: 
            sas_token = self.generate_sas_token(container_name, blob_name)
        else:
            sas_token = sas_token_pass
        return BlobClient(
            account_url=account_url,
            container_name=container_name,
            blob_name=blob_name,
            credential=sas_token  # Use the SAS token as the credential
        )

    def read_logs(self):
        visited = set()
        log_container = self.get_blob_client("logs", self.log)
        if log_container.exists():
            blob_content = log_container.download_blob()
            for line in blob_content.readall().decode('utf-8').splitlines():
                visited.add(line.strip())
            return visited
        else:
            return set()

    async def save_visited_urls(self, container_name):
        # Save visited URLs to Azure Blob Storage
        try:
            blob_container_client = self.get_blob_client(container_name, self.log)
            existing_blob_content = await blob_container_client.download_blob().readall()
            updated_blob_content = existing_blob_content + "\n" + "\n".join(self.visited)
            blob_container_client.upload_blob(updated_blob_content, overwrite=True)
        except Exception as e:
            raise e

        # Save rejected URLs to Azure Blob Storage
        try:
            blob_container_client = self.get_blob_client(container_name, self.failure_log)
            existing_blob_content = await blob_container_client.download_blob().readall()
            updated_blob_content = existing_blob_content + "\n" + "\n".join(self.rejected)
            blob_container_client.upload_blob(updated_blob_content, overwrite=True)
        except Exception as e:
            raise e

    async def get_docs_to_process(self, container_name):
        blob_container_client = self.blob_service_client.get_container_client(container_name)

        async for blob in blob_container_client.list_blobs():
            if blob.name.endswith('.json'):
                self.file_list.append(blob.name)


    async def read_page_content_and_enqueue(self, container_name):

        async def process_blob(blob_name):
            
            blob_client = BlobClient(
                account_url=account_url,
                container_name=container_name,
                blob_name=blob_name,
                credential=SAS_TOKEN  # Use the SAS token for the container
            )
            try:
                blob_content = blob_client.download_blob()
                data = json.loads(blob_content.readall().decode('utf-8'))
                page_content = data.get('page_content')
                if page_content:
                    with self.docs_lock:
                        self.docs.put((data, blob_name))
                else:
                    self.rejected.add(blob_name)
            except Exception as e:
                # Handle any exceptions that may occur
                print(f"Error reading blob {blob_name}: {str(e)}")

        # Create tasks to process blobs concurrently
        tasks = [process_blob(blob_name) for blob_name in self.file_list]
        await asyncio.gather(*tasks)

        for _ in self.threads:
            self.docs.put((None,None))

    def save_json(self, data, filename, container_name):
        blob_client = self.get_blob_client(container_name, filename)
        json_data = json.dumps(data, ensure_ascii=False, indent=4)
        blob_client.upload_blob(json_data, overwrite=True)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    fl = FileLogger(visited_log='visited.txt', rejected_log='rejected.txt', credentials=AZURE_STORAGE_ACCOUNT_CRED,
                    account_url=account_url)
    loop.run_until_complete(fl.get_docs_to_process("index-upload"))
    loop.run_until_complete(fl.read_page_content_and_enqueue("index-upload"))
    loop.close()
