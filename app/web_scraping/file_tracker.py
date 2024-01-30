import os
import json
from datetime import datetime, timedelta
from queue import Queue
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import BlobSasPermissions, generate_blob_sas, BlobClient

from dotenv import load_dotenv

load_dotenv()

AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
AZURE_STORAGE_ACCOUNT_CRED = os.getenv("AZURE_STORAGE_ACCOUNT_CRED")
AZURE_STORAGE_CONTAINER=os.getenv("AZURE_STORAGE_CONTAINER")

account_url = f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net"

# Define the expiry time for the SAS token (e.g., 1 hour from now)
expiry_time = datetime.utcnow() + timedelta(hours=1)

# Define the permissions for the SAS token (e.g., read access)
permissions = BlobSasPermissions(read=True)



class FileLogger():
    def __init__(self, visited_log, rejected_log, credentials, account_url):
        self.credentials=credentials
        self.account_url = account_url
        self.log = visited_log
        self.failure_log = rejected_log
        self.file_list = []
        self.docs = Queue()
        self.visited = self.read_logs()
        self.rejected = set()
        self.blob_service_client = BlobServiceClient(
                account_url=self.account_url,
                credential=self.credentials,
            )

    def generate_sas_token(self, cname, bname=None):
        # Generate the SAS token
        return generate_blob_sas(
            account_name= self.blob_service_client.account_name,
            container_name=cname,
            blob_name=bname,
            account_key=self.credentials,
            permission=permissions,
            expiry=expiry_time
        )

    def get_blob_client(self, container_name, blob_name):
        sas_token = self.generate_sas_token(container_name, blob_name)
        return BlobClient(
            account_url=account_url,
            container_name=container_name,
            blob_name=blob_name,
            credential=sas_token  # Use the SAS token as the credential
        )
      
    async def read_logs(self):
        visited = set()
        log_container = self.get_blob_client("logs", self.log)
        if log_container.exists():
            blob_content = await log_container.download_blob()
            for line in blob_content.readall().decode('utf-8').splitlines():
                visited.add(line.strip())
            return visited
        else:
            return set()
        
    def save_visited_urls(self, container_name):
            # Save visited URLs to Azure Blob Storage
            blob_container_client = self.get_blob_client(container_name, self.log)
            visited_blob_content = "\n".join(self.visited)
            blob_container_client.upload_blob(visited_blob_content, overwrite=True)

            # Save rejected URLs to Azure Blob Storage
            failure_blob_client = self.get_blob_client(container_name, self.failure_log)
            failure_blob_content = "\n".join(self.rejected)
            failure_blob_client.upload_blob(failure_blob_content, overwrite=True)

    async def get_docs_to_process(self, container_name):
        blob_container_client =  self.blob_service_client.get_container_client(container_name)
        async for blob in blob_container_client.list_blobs():
            if blob.name.endswith('.json'):
                self.file_list.append(blob.name)
        return

    def read_page_content_and_enqueue(self, container_name):
        content_queue = Queue()

        for filename in self.file_list:
            blob_client = self.get_blob_client(container_name, filename)
            try:
                blob_content = blob_client.download_blob()
                data = json.loads(blob_content.readall().decode('utf-8'))
                page_content = data.get('page_content')
                if page_content:
                    content_queue.put((data, filename))
                else:
                    self.rejected.add(filename)
            except Exception as e:
                # Handle any exceptions that may occur du
                print(f"Error reading blob {filename}: {str(e)}")

            self.docs = content_queue
            return

    def save_json(self, data, filename, container_name):
        blob_client = self.get_blob_client(container_name, filename)
        json_data = json.dumps(data, ensure_ascii=False, indent=4)
        blob_client.upload_blob(json_data, overwrite=True)


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    fl = FileLogger(visited_log='visited.txt', rejected_log='rejected.txt', credentials=AZURE_STORAGE_ACCOUNT_CRED, account_url=account_url)
    print(loop.run_until_complete(fl.get_docs_to_process("index-upload")))

    loop.close()