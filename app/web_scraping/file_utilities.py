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
    parts = filename.replace('_2F', '/').split('/')
    parts = parts[:-2]
    return parts

def count_prefixes(directory):
    prefix_counter = Counter()
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            prefixes = extract_prefixes(filename)
            prefix_key = '/'.join(prefixes)
            prefix_counter[prefix_key] += 1
    return prefix_counter

def get_duplicate_index(full_list, subsequence):
    len_sub = len(subsequence)
    len_full = len(full_list)
    for i in range(len_full - len_sub + 1):
        check_sequence = full_list[i:i+len_sub]
        if check_sequence == subsequence:
            return i
    return -1

def find_divergence_point(set1, set2):
    min_length = min(len(set1), len(set2))
    for i in range(min_length):
        first_word = set1[i]
        second_word = set2[i]
        if first_word != second_word or i == min_length:
            return i
    return -1

def remove_duplicate_passages(text):
    words = text.split()
    passage_length = 20
    step_length = 5
    total_length = len(words)
    found_char_index = -1
    i = 0
    loop_safety_counter = 0

    if total_length > 5000:
        # skip checking very long passages (likely anomalies anyway)
        return

    while i <= (total_length - passage_length) and loop_safety_counter<1000:
        #handle malformed text
        if words[i].startswith("."): 
            i += 1
            continue

        current_passage_words = words[i:i + passage_length]
        current_passage_text = ' '.join(current_passage_words)
        remaining_passage_words = words[i + passage_length:]
        remaining_passage_text = ' '.join(remaining_passage_words)
        found_char_index = remaining_passage_text.find(current_passage_text)


        if found_char_index != -1:
            # Calculate the actual index of the found duplicate in the remaining passage
            duplicate_index = get_duplicate_index(remaining_passage_words, current_passage_words)
            # add back starting point to get index in words
            duplicate_index = duplicate_index + i + passage_length
            pre_dup_words = words[i:duplicate_index]
            post_dup_words = words[duplicate_index:]
            divergence_length = find_divergence_point(pre_dup_words, post_dup_words)

            if divergence_length == 0: 
                print("#### Error in dup checking, no duplicate found! likely malformed text.  Skipping. ")
            #add back i to include full word list:
            divergence_point = divergence_length + duplicate_index
            # Remove the duplicate passage
            if divergence_point <= total_length and divergence_length>0:
                print(f"removing current passage: {current_passage_text} from remaining text - duplicate passage is {' '.join( words[duplicate_index:divergence_point])}")
                del words[duplicate_index:divergence_point]
                total_length = len(words)
            elif divergence_point == total_length:
                #passages don't diverge for the remainder of the text (edge case)
                del words[duplicate_index:]
                break
            else:
                print("######## error in duplication check, skipping")
                break

        else:
            i += step_length
        
        loop_safety_counter += 1

    return ' '.join(words)

if __name__ == "__main__":
    out = count_prefixes('/Users/marynelson/docs')
    print(out)
