import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import time
import threading
import sys
from config import USER_AGENT, DELAY_BETWEEN_REQUESTS, MAX_DEPTH, DOWNLOAD_FOLDER, MAX_FILE_SIZE

class WebCrawler:

    #WebCrawler initialization
    def __init__(self, base_url, page_keywords=None):
        self.crawl_path = {}  # Track the path: {url: parent_url}
        self.base_url = base_url # Base URL to start crawling 
        self.visited_urls = set() # Set to keep track of visited URLs
        self.page_keywords = page_keywords or []  # Keywords to filter HTML pages to visit
        self.found_links = set() # Set to keep track of found links
        self.session = requests.Session() # Initialize a session for making requests
        self.session.headers.update({'User-Agent': USER_AGENT}) # Initialize session with user agent
        self.stop_crawling = False  # Flag to stop crawling


    # Start a thread to monitor user input for stopping the crawler
    def start_input_monitor(self):
        def monitor():
            try:
                input("Press Enter to stop crawling...\n\n")
                self.stop_crawling = True
                print("Stopping crawling... will finish current requests.")
            except:
                pass

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

    # Verify if the URL is within the same domain as the base URL
    def is_same_domain(self, url):
       
        try:
            base_domain = urlparse(self.base_url).netloc
            url_domain = urlparse(url).netloc
            
            # Simply check if domains match - no other restrictions
            return base_domain == url_domain
            
        except Exception:
            return False
    

    # Get the web page content
    def get_page(self,url):

        try:
            # Show the crawled path
            if url in self.crawl_path:
                parent = self.crawl_path[url]
                print(f"Visiting: {url} → (from {parent})")
            else:
                print(f"Visiting: {url} → (starting point)")


            response = self.session.get(url, timeout=10) # Get the page content with a timeout
            response.raise_for_status()  # Raise an error for bad responses

            # Check if the content type is HTML
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser') # Parse the HTML content
            time.sleep(DELAY_BETWEEN_REQUESTS)  # Delay between requests to avoid overloading the server
            return soup
        
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None


       
    # Extract links from the page content
    def extract_links(self, soup, current_url):

        links = set()

        # Try to find links only in content areas (safer approach)
        content_selectors = [
            'main', 'article', '.content', '#content', '.main-content', 
            '#main-content', '.post-content', '.entry-content', '.page-content'
        ]

        content_links = []
        for selector in content_selectors:
            content_areas = soup.select(selector)
            if content_areas:
                print(f"DEBUG - Found content area: {selector}")
                for area in content_areas:
                    content_links.extend(area.find_all('a', href=True))
                break  # Use first found content area

        # If no content area found, use all links but exclude navigation
        if not content_links:
            print("DEBUG - No content area found, using all links")
            all_links = soup.find_all('a', href=True)
            # Filter out links from navigation areas
            nav_areas = soup.select('nav, header, footer, [class*="menu"], [class*="nav"]')
            nav_links = set()
            for nav in nav_areas:
                nav_links.update(nav.find_all('a', href=True))
            content_links = [link for link in all_links if link not in nav_links]


        # Find all anchor tags with href attributes
        for link in content_links:
            href = link['href']

            # Convert relative URLs to absolute URLs
            absolute_url = urljoin(current_url, href)

            # Remove fragments from the URL
            parsed_url = urlparse(absolute_url)
            clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, parsed_url.query, ''))

            # Check if the URL is within the same domain
            if self.is_same_domain(clean_url):
                # Check if the URL matches the page keywords
                if self.matches_page_keywords(clean_url):

                    links.add(clean_url)
                    self.found_links.add(clean_url)
        
        return links
    

    # Check if the URL matches the page keywords
    def matches_page_keywords(self, url):
        
            return True
        


    # Primary method to crawl the web starting from the base URL
    def crawl(self, base_url, max_depth=MAX_DEPTH):

        print(f"Starting crawl from: {base_url}") # Initialize the stack with the base URL and depth
        urls_to_visit = [(base_url, 0)] # (url, depth)

        # Start a thread to monitor user input for stopping the crawler
        self.start_input_monitor()
    

        # Loop through the URLs to visit
        while urls_to_visit and not self.stop_crawling:
            current_url, depth = urls_to_visit.pop(0)

            #check if the URL has already been visited
            if current_url in self.visited_urls:
                continue
    
            # Check if the maximum depth has been reached
            if depth > max_depth:
                continue

            # Mark the URL as visited
            self.visited_urls.add(current_url)

            # Get the page content
            soup = self.get_page(current_url)
            if soup is None:
                continue

            # Extract links from the page content
            links = self.extract_links(soup, current_url)

            for link in links:
                if link not in self.visited_urls:
                    urls_to_visit.append((link, depth + 1))
                    self.crawl_path[link] = current_url#  # Track the path: remember where this link came from

        print(f"Crawling completed. Found {len(self.found_links)} links.")
        print(f"Visited {len(self.visited_urls)} URLs.")
