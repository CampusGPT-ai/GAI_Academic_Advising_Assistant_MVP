from web_scraping.dns_resolver import find_all_subdomains
from web_scraping.apify_page_count import get_content

from settings.settings import Settings
settings = Settings()

URL_DOMAIN = "bryanuniversity.edu"

exclusion_list = [
"www",
"src",
]

url_list = find_all_subdomains(URL_DOMAIN)#[{"url": "https://src.bryanuniversity.edu"}]#

for item in exclusion_list:
    for url in url_list:
        if item in url["url"]:
            url_list.remove(url)
            break

results = []
for url in url_list:
    results.append(get_content(url["url"]))

print(results)