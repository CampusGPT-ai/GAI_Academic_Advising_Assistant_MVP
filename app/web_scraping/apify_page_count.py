
from settings.settings import Settings
from apify_client import ApifyClient
from bs4 import BeautifulSoup
import asyncio
import requests
settings = Settings()
import pandas as pd
import numpy as np

def get_content(url):

    # Initialize the Apify client
    client = ApifyClient(settings.APIFY_TOKEN)
    starting_url = url

    # Define the actor's input
    actor_input = {
    "aggressivePrune": False,
    "clickElementsCssSelector": "[aria-expanded=\"False\"]",
    "clientSideMinChangePercentage": 15,
    "crawlerType": "playwright:adaptive",
    "debugLog": False,
    "debugMode": False,
    "ignoreCanonicalUrl": False,
    "proxyConfiguration": {
        "useApifyProxy": True
    },
    "readableTextCharThreshold": 100,
    "removeCookieWarnings": True,
    "removeElementsCssSelector": "nav, footer, script, style, noscript, svg,\n[role=\"alert\"],\n[role=\"banner\"],\n[role=\"dialog\"],\n[role=\"alertdialog\"],\n[role=\"region\"][aria-label*=\"skip\" i],\n[aria-modal=\"True\"]",
    "renderingTypeDetectionPercentage": 10,
    "saveFiles": False,
    "saveHtml": False,
    "saveHtmlAsFile": False,
    "saveMarkdown": True,
    "saveScreenshots": False,
    "startUrls": [
        {
        "url": starting_url
        },
    ],
    "useSitemaps": False,
    "includeUrlGlobs": [],
    "excludeUrlGlobs": [],
    "maxCrawlDepth": 20,
    "maxCrawlPages": 9999999,
    "initialConcurrency": 0,
    "maxConcurrency": 200,
    "initialCookies": [],
    "maxSessionRotations": 10,
    "maxRequestRetries": 5,
    "requestTimeoutSecs": 60,
    "minFileDownloadSpeedKBps": 128,
    "dynamicContentWaitSecs": 10,
    "maxScrollHeightPixels": 5000,
    "htmlTransformer": "readableText",
    "maxResults": 1000,
    }

    # Run the actor and wait for it to finish
    actor = client.actor("apify/website-content-crawler")
    run = actor.call(run_input=actor_input)

    # Fetch the results
    results = client.dataset(run["defaultDatasetId"]).list_items().items

    # Sum up the link counts to get an estimate
    return results

def download_results(dataset_id):

    # Define the base URL and the parameters
    base_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
    params = {
        "token": "apify_api_L3Y5KT0rNXHKAvTzco6UgME8TDKRda431ZC7"
    }

    # Make the GET request
    response = requests.get(base_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Print the JSON response
        return response.json()
    else:
        # Print the error message
        print(f"Failed to retrieve data: {response.status_code}")
        print(response.text)

def get_runs():
        # Define the base URL and the parameters
    base_url = f"https://api.apify.com/v2/actor-runs"
    params = {
        "token": "apify_api_L3Y5KT0rNXHKAvTzco6UgME8TDKRda431ZC7"
    }

    # Make the GET request
    response = requests.get(base_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Print the JSON response
        result = response.json()
        return result.get('data').get('items')
    else:
        # Print the error message
        print(f"Failed to retrieve data: {response.status_code}")
        print(response.text)

def get_run_inputs(run_id):
 #https://api.apify.com/v2/key-value-stores/kMzszX4a1gODsY6qm/records/INPUT?token=apify_api_L3Y5KT0rNXHKAvTzco6UgME8TDKRda431ZC7
         # Define the base URL and the parameters
    base_url = f"https://api.apify.com/v2/key-value-stores/{run_id}/records/INPUT"
    params = {
        "token": "apify_api_L3Y5KT0rNXHKAvTzco6UgME8TDKRda431ZC7"
    }

    # Make the GET request
    response = requests.get(base_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Print the JSON response
        result = response.json()
        return result.get('startUrls')
    else:
        # Print the error message
        print(f"Failed to retrieve data: {response.status_code}")
        print(response.text)

def run_all(domain: str, exclusion_list: list) -> list:
    result = get_runs()
    run_ids = []
    valid_runs = set()
    downloaded_results = []
    for item in result:
        run_ids.append(item.get('defaultKeyValueStoreId'))

    for item in result:
        result_urls = get_run_inputs(item.get('defaultKeyValueStoreId'))
        for url in result_urls:
            url_str = url.get('url')
            if domain in url_str and not any(exclusion in url_str for exclusion in exclusion_list):
                valid_runs.add(item.get('defaultDatasetId'))

    for run_item in valid_runs:
        r = download_results(run_item)

        for i in r:
            metadata: dict = i['metadata']
            graph = {}
            description: str = ''
            if metadata.get('jsonLd'):
                json: dict = metadata.get('jsonLd')[0]
                if not isinstance(json, dict):
                    continue
                if json.get('@graph'):
                    graph = json.get('@graph')
                    for g in graph:
                        if g.get('@type') == 'WebPage':
                            graph = g
                        if g.get('@type') == 'WebSite':
                            description = g.get('description')
                    if isinstance(graph, list):
                        graph = {}

            flat_results = {
                'markdown': i['markdown'],
                'canonicalUrl': metadata.get('canonicalUrl'),
                'dateModified': graph.get('dateModified'),
                'title': graph.get('name'),
                'description': description,
            }
            downloaded_results.append(flat_results)

    return downloaded_results

def process_results(results: list) -> list:
    df = pd.DataFrame(results)

    from datetime import datetime
    # Function to calculate time since modified date
    def time_since_modified(modified_date_str):
        if not isinstance(modified_date_str, str):
            return 0
        if modified_date_str == "":
            return 0
        if isinstance(modified_date_str, str):
            try:
                modified_date = datetime.strptime(modified_date_str, "%Y-%m-%dT%H:%M:%S%z")
                current_date = datetime.now(modified_date.tzinfo)  # Ensure the same timezone
                time_difference = current_date - modified_date
                return time_difference.days
            except:
                return 0

    import re
    # Function to calculate content metrics
    def calculate_content_metrics(markdown):
            # Replace URLs with a placeholder
        if not isinstance(markdown, str):
            return pd.Series([0, 0, 0, 0, 0, 0, 0, 0])
        
        if markdown == "":
            return pd.Series([0, 0, 0, 0, 0, 0, 0, 0])
        
        if len(markdown) <10:
            return pd.Series([0, 0, 0, 0, 0, 0, 0, 0])
        
        url_placeholder = "URL_PLACEHOLDER"
        urls = re.findall(r'https?://[^\s]+', markdown)
        for url in urls:
            markdown = markdown.replace(url, url_placeholder)
            
        word_count = len(markdown.split())
        sentence_count = len(re.split(r'[.!?]+', markdown))
        char_count = len(markdown)
        average_word_length = sum(len(word) for word in markdown.split()) / word_count
        average_sentence_length = word_count / sentence_count if sentence_count else 0
        header_count = markdown.count('#')
        list_count = len(re.findall(r'^[*-]\s', markdown, re.MULTILINE))
        link_count = len(re.findall(r'\[.*?\]\(.*?\)', markdown))
        return pd.Series([word_count, sentence_count, char_count, average_word_length, average_sentence_length, header_count, list_count, link_count])
    
    import tldextract
    from urllib.parse import urlparse

    def link_depth_class(link_depth):
        if link_depth < 2:
            return 2
        elif link_depth == 2:
            return 1
        elif link_depth> 2:
            return 0
        else:
            return 0
        
    def age_class(age):
        if age < 365:
            return 2
        elif age < 720:
            return 1
        else:
            return 0
        
    def sentence_count_class(sc):
        if sc < 5:
            return 0
        elif sc < 20:
            return 1
        elif sc > 50:
            return 2
        else:
            return 0

    def extract_parts(url):
        extracted = tldextract.extract(url)
        subdomain = extracted.subdomain if extracted.domain == "ucf" and extracted.suffix == "edu" else None

        # Extract the first path item
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        first_path_item = path_parts[0] if path_parts else None
        second_path_item = path_parts[1] if len(path_parts) > 1 else None
        link_depth = len(path_parts)
        
        return pd.Series([subdomain, first_path_item, second_path_item, link_depth])
    
    import tiktoken

    def split_markdown_content(df, token_limit=5000, overlap_ratio=0.2):
        # Initialize the tokenizer
        enc = tiktoken.get_encoding('cl100k_base')  # Use the appropriate encoding

        def split_content(content):
            tokens = enc.encode(content)
            token_count = len(tokens)

            if token_count <= token_limit:
                return [content]

            chunk_size = int(token_limit * (1 - overlap_ratio))
            overlap_size = int(token_limit * overlap_ratio)
            chunks = []

            start = 0
            while start < token_count:
                end = start + token_limit
                chunk_tokens = tokens[start:end]
                chunk_text = enc.decode(chunk_tokens)
                chunks.append(chunk_text)
                start += chunk_size

            return chunks

        new_rows = []
        for _, row in df.iterrows():
            markdown_content = row['markdown']
            chunks = split_content(markdown_content)
            for chunk in chunks:
                new_row = row.copy()
                new_row['markdown'] = chunk
                new_rows.append(new_row)

        new_df = pd.DataFrame(new_rows)
        return new_df
    
    df= df.drop_duplicates(subset=['markdown'], keep='first')
    df = df[df['markdown'] != '']
    print(df.shape)
    df['days_since_modified'] = df['dateModified'].apply(lambda x: time_since_modified(x))
    df = df[df['days_since_modified'] < 731]
    print(df.shape)
    df[['word_count', 'sentence_count', 'char_count', 'average_word_length', 'average_sentence_length', 'header_count', 'list_count', 'link_count']] = df['markdown'].apply(calculate_content_metrics)
    df = df[df['word_count'] > 5]
    print(df.shape)
    df[['subdomain', 'first_path_item', 'second_path_item', 'link_depth']] = df['canonicalUrl'].apply(lambda x: extract_parts(x))
    df['sentence_count_class'] = df['sentence_count'].apply(sentence_count_class)
    df['age_class'] = df['days_since_modified'].apply(age_class)
    df['link_depth_class'] = df['link_depth'].apply(link_depth_class)
    df = split_markdown_content(df)

    return df


if __name__=="__main__":
    results = run_all('ucf.edu', ['events', 'news', 'publication'])
    df = process_results(results)