
from googleapiclient.discovery import build
import json, os
from web_scraping.scrape import Crawler
from dotenv import load_dotenv
load_dotenv()
import asyncio
import unidecode
# API Key for accessing the Google API
CSE_KEY = os.getenv("GOOGLE_CSE_ID")
API_KEY = os.getenv("GOOGLE_API_KEY")

# Function to perform the Google API query
def google_search(query, num_results=3):
    try:
        service = build('customsearch', 'v1', developerKey=API_KEY)
        result = service.cse().list(q=query, cx=CSE_KEY, num=num_results).execute()
    except Exception as e:
        print("Error in google_search: " + str(e))
        result['items'] = None
    # Extract and return the search results
    return result['items']

# Main function to run the script
def query_google(text, queue=None, num_results=3):
    # Get the query from the user
    query = text
    dict_result = []
    # Perform the Google API search and retrieve only the top 3 results
    try:
        results = google_search(query, num_results)
        for index,result in enumerate(results,0):
            dict_result.append(result)
            
        output_list = [(x['link'] + ": " + x['snippet']) for x in dict_result]
        combined_output = "google: " + '\n'.join(output_list)
    except Exception as e:
        print("Error in query_google: " + str(e))
        combined_output = None
    if queue:
        queue.put(combined_output)
        return None
    else:
        return dict_result
    

# Run the script
if __name__ == '__main__':
    
    def query(text):
        results = query_google(text)
        return results

    results = query('When is biochemistry 1 offered?')
    print(results)

    for x in results:
        url = x["link"]
        crawler = Crawler(starting_url=url, directory=None, visited_log=None)
        urls, content, metadata = asyncio.run(crawler.crawl_single_page(url))
        content = crawler.extract_text_from_html(content)
        content = crawler.remove_extra_line_breaks(content)
        content =  unidecode(content)
        content = content.replace('\n', ' ').replace('\t',' ').replace('\'',' ').replace('\"',' ')
        print(content)

    