
from urllib.parse import urlparse, urljoin, quote
from bs4 import BeautifulSoup
import requests, json, re
from playwright.async_api import async_playwright
import os, asyncio
from langchain.docstore.document import Document
from datetime import datetime
from queue import Queue
from unidecode import unidecode

DOCUMENT_DIRECTORY = '/Users/marynelson/docs/itech_catalog'
VISITED_LOG = '/Users/marynelson/docs/itech_catalog/logs/visited.txt'
REJECTED_LOG = '/Users/marynelson/docs/itech_catalog/logs/rejected.txt'
SELECTOR = '.acalog-course'
# 'a[onclick*="showCatalogData"]'
MAIN_PAGE = '#kuali-catalog-main'
# <div name="ACG - Accounting General" class="style__collapsibleBox___15waq"><div class="style__header___2lB0y style__headerExpandable___2d4hu"><div style="flex: 2 1 0%;"><h2 class="style__title___3KgQi">ACG - Accounting General</h2><div class="style__subtitle___BSfwg"></div></div><a aria-hidden="true" target="_blank" tabindex="-1" class="style__linkButton___2NRHE" href="https://www.ucf.edu/catalog/undergraduate/#/courses?group=ACG%20-%20Accounting%20General"><button tabindex="-1" aria-label="Link to ACG - Accounting General" aria-hidden="true" type="button" class="md-btn md-btn--icon md-pointer--hover md-inline-block"><div class="md-ink-container"></div><i class="md-icon material-icons md-text--inherit">open_in_new</i></button></a><button aria-controls="ACG - Accounting General" aria-expanded="false" aria-label="show  ACG - Accounting General" type="button" class="md-btn md-btn--icon md-pointer--hover md-inline-block style__collapseButton___12yNL"><div class="md-ink-container"></div><i class="md-icon material-icons md-text--inherit">keyboard_arrow_down</i></button></div></div>
class Crawler():
    def __init__(
        self,
        starting_url: str,
        directory: str,
        visited_log: str
    ):
        self.directory = directory
        self.links = Queue()
        self.links.put(starting_url)
        self.visited = set()
        self.log = visited_log
        self.rejected = set()
        self.usera = (
            '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'''
            )

        # initialize list to last visited if it exists
        self.visited = self.read_visited_urls()
        self.all_links = set()
        
    def read_visited_urls(self):
        visited = set()
        if os.path.exists(self.log):
            with open(self.log, 'r') as file:
                for line in file:
                    visited.add(line.strip())   
            return visited
        else:
            return set()
        
    def read_scraped_files(self):
        json_files = [file for file in os.listdir(self.directory) if file.endswith('.json')]
        return json_files
    
    def save_visited_urls(self):
        with open(self.log, 'w') as file:
            for url in self.visited:
                file.write(f"{url}\n")
        
        with open(REJECTED_LOG, 'w') as file:
            for url in self.rejected:
                file.write(f"{url}\n")
    
    def read_all_links(self):
        with open('all_links.txt', 'r') as file:
            for line in file:
                self.all_links.add(line.strip())

    def save_all_links(self):
        with open('all_links.txt', 'w') as file:
            for link in self.all_links:
                file.write(f"{link}\n")

    def extract_sld_tld(self, url):
        """
        Extract the second-level domain (SLD) and top-level domain (TLD) from the URL.
        """
        domain_parts = urlparse(url).netloc.split('.')
        # Ensure that the domain has at least two parts
        if len(domain_parts) >= 2:
            return '.'.join(domain_parts[-2:])
        return ''
    
        
    async def fetch_selector(self, selector, page):
        selectors = await page.query_selector_all(selector)
        await asyncio.sleep(10)
        return selectors
    
    async def expand_all_menus(self, selectors, page):
        for selector in selectors:
            try:
                await selector.click()
                await asyncio.sleep(1)
            except:
                print("failed to click on selector for ", page.url)
        return page

    async def expand_left_menu(self, selectors, page):
        for selector in selectors:
            try:
                await selector.click()
                await asyncio.sleep(1)
                all_content = ''
                main_page = await page.query_selector_all(MAIN_PAGE)
                for elements in main_page:
                    html_content = await elements.inner_html()

                    content = self.extract_text_from_html(html_content)
                    content = self.remove_extra_line_breaks(content)
                    content =  unidecode(content)
                    content = content.replace('\n', ' ').replace('\t',' ').replace('\'',' ').replace('\"',' ')
                    all_content += content

                self.links.put(page.url)

                print(f'added link to list {page.url}')
            except:
                print("failed to click on selector for ", page.url)

 
    async def fetch_content_playwright(self, url):
        metadata = {"source": url}
    
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page(user_agent=self.usera)
                await page.set_viewport_size({"width": 1280, "height": 720}) #avoid hidden content with responsive design
                
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=20000) 
                except:
                    print("failed to load page")
                    self.rejected.add(url)
                    return None, None
                

                metadata["last_updated"] = datetime.now().isoformat()
                metadata["title"] = await page.title()
                meta_description = await page.query_selector('meta[name="description"]')

                #selectors_list = await self.fetch_selector(SELECTOR, page)

                #page = await self.expand_all_menus(selectors_list, page)   

                content = await page.content()

                await asyncio.sleep(10)

                if meta_description:
                    metadata["description"] = await meta_description.get_attribute('content')
                        
                await browser.close()
                return content, metadata
        except TimeoutError:
            self.rejected.add(url)
            print("Timeout occurred while loading the page.")
            return None
        except Exception as e:
            self.rejected.add(url)
            print(f"An error occurred: {e}")
            return None, None

    async def crawl_single_page(self, url, domain_sld_tld = None, same_domain = None, file_types = None):
        """
        Crawl a single page and get the page content.  
        1. check if page has already been visited, if not add move it from links to visited
        2. try using playwright to mock browser, if that fails, use simple request, if that fails, add link to rejected list
        3. augment links list with any new links found that haven't already been visited.
        """

        print(f"Crawling page {url}")
        
        try:
            content, metadata = await self.fetch_content_playwright(url)
        except Exception as e:
            print(f"failed to get content from playwright with exception: {e}")
            return None, None

        soup = BeautifulSoup(content, "html.parser")

        links = [urljoin(url, a.get('href'))
                for a in soup.find_all('a', href=True)]
        
        for link in links:
            self.all_links.add(link)
        
        self.save_all_links()

        # filtered_links = await self.filter_links(links, file_types, domain_sld_tld, same_domain)         
        return content, metadata

    async def crawl(self, file_types=None, same_domain=True):
        """
        Start crawling from the given URL. Main method for class. 

        Args:
            file_types (list, optional): List of file types to filter the crawled URLs. Defaults to None.
            same_domain (bool, optional): Flag to indicate whether to crawl only within the same domain. Defaults to True.
        """
        already_scraped = self.read_scraped_files()
        self.read_all_links()

        for link in self.all_links:
            self.links.put(link)
        
        try:    
            while not self.links.empty():
                current_url = self.links.get()
                filename = f"{self.url_to_filename(current_url)}.json"
                print(f'crawling {current_url}')
                
                if current_url in self.visited or filename in already_scraped:
                    print("skipping file for ", filename)
                    if self.links.qsize()!=0: 
                        continue
                
                self.visited.add(current_url)
                
                domain_sld_tld = self.extract_sld_tld(current_url)
                try:
                    content, metadata = await self.crawl_single_page(current_url, domain_sld_tld, same_domain, file_types)
                except Exception as e:
                    print(f"failed to crawl page {e}")
                    continue
                 
                content = self.extract_text_from_html(content)
                content = self.remove_extra_line_breaks(content)
                content =  unidecode(content)
                content = content.replace('\n', ' ').replace('\t',' ').replace('\'',' ').replace('\"',' ')
                self.save_to_file(current_url, content, metadata)
                self.save_visited_urls()

        except KeyboardInterrupt:  
            print("program interrupted, saving urls")  
            self.save_visited_urls()

    
    def remove_extra_line_breaks(self, markdown_content: str) -> str:
        """
        Removes extra line breaks from the given Markdown content.
        Where there are one or more line breaks, leaves one but gets rid of the extras.
        """
        cleaned_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
        return cleaned_content    

    def extract_text_from_html(self, html_content):
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script_or_style in soup(['script', 'style']):
            script_or_style.extract()

        # Get text
        text = soup.get_text()

        # Break into lines and remove leading/trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text
    
    def save_to_file(self, url, content, metadata):
        try: 
            if content is not None:
                
                doc =  Document(page_content=content, metadata=metadata)
                filename = f"{self.url_to_filename(url)}.json"
                try: 
                    with open(os.path.join(DOCUMENT_DIRECTORY,
                                        filename), "w") as f:
                        json.dump(doc.__dict__, f)
                except Exception as e: 
                    raise e
        except Exception as e: 
            print(f"Error crawling page: {e.__str__}")
            self.rejected.add(url)
            return []

    def url_to_filename(self, url):
        # Remove the protocol part of the URL (http:// or https://)
        if url.startswith('http://'):
            url = url[7:]
        elif url.startswith('https://'):
            url = url[8:]

        # Encode the URL to be filesystem-safe
        # Replace filesystem-illegal characters (e.g., '/', ':', '?') with an underscore or other safe character
        # Here we use `quote` which percent-encodes the string, and then replace '%' with '_' to make it more readable
        # This encodes everything except for letters, digits and '_-.'.
        filename = quote(url, safe='')
        if len(filename) > 255:
            filename = filename[:100] + filename[-25:]
        # Replace '%' to ensure the filename is filesystem-safe
        filename = filename.replace('%', '_')

        return filename

# Example usage:
if __name__ == '__main__':
    url = '''https://catalog.indianatech.edu/index.php?'''
    crawler = Crawler(starting_url=url, directory=DOCUMENT_DIRECTORY, visited_log=VISITED_LOG)
    asyncio.run(crawler.crawl())
   
            
