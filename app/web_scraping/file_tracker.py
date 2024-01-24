import os
import json
from queue import Queue

class FileLogger():
    def __init__(self, document_directory, visited_log, rejected_log, unprocessed_directory):
        self.directory = document_directory
        self.dir_in = unprocessed_directory
        self.log = visited_log
        self.failure_log = rejected_log
        self.file_list = []
        self.docs = Queue()
        self.visited = self.read_visited_urls()
        self.rejected = set()
        
        
    def read_visited_urls(self):
        visited = set()
        if os.path.exists(self.log):
            with open(self.log, 'r') as file:
                for line in file:
                    visited.add(line.strip())   
            return visited
        else:
            return set()
        
    def save_visited_urls(self):
        with open(self.log, 'w') as file:
            for url in self.visited:
                file.write(f"{url}\n")
        
        with open(self.failure_log, 'w') as file:
            for url in self.rejected:
                file.write(f"{url}\n")
        
    def get_docs_to_process(self):
        json_files = [file for file in os.listdir(self.dir_in) if file.endswith('.json')]
        self.file_list = [file for file in json_files if file not in self.visited]
        self.file_list = json_files
        return
        
    def read_page_content_and_enqueue(self):
        """
        Reads the page content from files in the specified directory and enqueues them in a content queue.

        Args:
            directory (str): The directory path where the files are located. Defaults to UNPROCESSED_DIRECTORY.

        Returns:
            None
        """
        content_queue = Queue()

        for filename in self.file_list:
            full_path = os.path.join(self.dir_in, filename)
            with open(full_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                page_content = data.get('page_content')
                if page_content:
                    content_queue.put((data, filename))
                else: 
                    self.rejected.add(filename)
                    
        self.docs = content_queue
        return
    
    def save_json(self, data, filename):
        with open(os.path.join(self.directory, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    