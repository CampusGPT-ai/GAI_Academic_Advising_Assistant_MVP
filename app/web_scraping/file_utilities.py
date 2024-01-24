import os
import json
from pathlib import Path
from collections import Counter

def delete_files_without_content(directory):
    files_to_delete = []

    # First, identify files to delete
    for filename in os.listdir(directory):
        file_path = Path(directory) / filename
        if filename.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    if not data.get('page_content'):
                        files_to_delete.append(file_path)
                except json.JSONDecodeError:
                    print(f"Error reading JSON file: {filename}")

    # Now, delete the files
    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            print(f"Deleted file: {file_path.name}")
        except PermissionError:
            print(f"Permission denied: Could not delete {file_path.name}. File might be in use.")

def extract_prefixes(filename):
    parts = filename.split('.ucf.edu')[0]
    return parts.split('.')

def count_prefixes(directory):
    prefix_counter = Counter()
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            prefixes = extract_prefixes(filename)
            prefix_key = '.'.join(prefixes)
            prefix_counter[prefix_key] += 1
    return prefix_counter

def remove_duplicate_passages(text):
    words = text.split()
    passage_length = 10
    total_length = len(words)
    i = 0

    while i <= len(words) - passage_length and len(words) < 5000:
        current_passage = ' '.join(words[i:i + passage_length])
        remaining_text = ' '.join(words[i + passage_length:])

        found_index = remaining_text.find(current_passage)
        if found_index != -1:
            # Calculate the actual index of the found duplicate in the original list
            duplicate_index = i + passage_length + found_index // (passage_length + 1)
            # Remove the duplicate passage
            del words[duplicate_index:duplicate_index + passage_length]

        else:
            i += passage_length  # Move forward by ten words

    return ' '.join(words)

