import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import time
import threading
import sys
from config import USER_AGENT, DELAY_BETWEEN_REQUESTS, MAX_DEPTH, DOWNLOAD_FOLDER, MAX_FILE_SIZE
import logging
from tqdm import tqdm


logger = logging.getLogger('crawler')  # Initialize a logger for the crawler



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
                logger.info("Stopping crawling... will finish current requests.")
            except:
                logger.error("Error in input monitor thread")  # Log any error in the input monitor thread
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
                logger.info(f"Visiting: {url} → (from {parent})")
            else:
                logger.info(f"Visiting: {url} → (starting point)")


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
            logger.error(f"Error fetching {url}: {e}")
            return None


       
    # Extract links from the page content
    def extract_links(self, soup, current_url):

        links = set()

        # Try to find links only in content areas (safer approach)
        content_selectors = [
            'main', 'article', '.content', '#content', '.main-content', 
            '#main-content', '.post-content', '.entry-content', '.page-content',
            '.main', '.container .content', '.site-content', '.primary-content'
        ]

        content_links = []
        for selector in content_selectors:
            content_areas = soup.select(selector)
            if content_areas:
                logger.debug(f"Found content area: {selector}")
                for area in content_areas:
                    content_links.extend(area.find_all('a', href=True))
                break  # Use first found content area

        # If no content area found, use all links but exclude navigation
        if not content_links:
            logger.debug("No content area found, applying aggressive navigation filter")
            all_links = soup.find_all('a', href=True)
            
            # Selectors for excluding navigation areas (more comprehensive)
            nav_selectors = [
                'nav', 'header', 'footer', 'aside', '.sidebar',
                '[class*="menu"]', '[class*="nav"]', '[class*="header"]', 
                '[class*="footer"]', '[class*="sidebar"]', '[class*="widget"]',
                '[id*="menu"]', '[id*="nav"]', '[id*="header"]', '[id*="footer"]',
                '.breadcrumb', '.pagination', '.social', '[class*="social"]',
                '.tags', '[class*="tag"]', '.categories', '[class*="categor"]',
                '.search', '[class*="search"]', '.login', '[class*="login"]'
                '.header-menu', '#header-menu', '[class*="header-menu"]',
                '.top-menu', '#top-menu', '[class*="top-menu"]',
                '.main-menu', '#main-menu', '[class*="main-menu"]',
                '.primary-menu', '#primary-menu', '[class*="primary-menu"]'
            ]
            
            # Find all links in navigation areas
            excluded_links = set()
            for selector in nav_selectors:
                nav_areas = soup.select(selector)
                for nav in nav_areas:
                    excluded_links.update(nav.find_all('a', href=True))
            
            # Filter out navigation links       
            navigation_keywords = [
                'home', 'homepage', 'contatti', 'about', 'chi siamo', 'privacy',
                'cookie', 'termini', 'condizioni', 'login', 'accedi', 'registrati',
                'menu', 'navigation', 'naviga', 'cerca', 'search', 'social',
                'facebook', 'twitter', 'instagram', 'youtube', 'linkedin'
            ]
            
            content_links = []

            # Filter links to exclude navigation and unwanted keywords    
            for link in all_links:
                
                # Skip if the link is in the excluded links
                if link in excluded_links:
                    continue

                # Check if the link text contains navigation keywords
                link_text = link.get_text(strip=True).lower()
                if any(keyword in link_text for keyword in navigation_keywords):
                    continue

                # Check if the link has a class or id that indicates navigation
                link_classes = ' '.join(link.get('class', [])).lower()
                link_id = link.get('id', '').lower()
                if any(nav_word in link_classes or nav_word in link_id 
                    for nav_word in ['menu', 'nav', 'header', 'footer', 'social']):
                    continue
                
                content_links.append(link)

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
        
        # Log statistics
        logger.debug(f"Found {len(content_links)} links in content area")
        logger.debug(f"After filtering: {len(links)} valid links added")

        return links
    

    # Check if the URL matches the page keywords
    def matches_page_keywords(self, url):
        # If no page keywords are specified, accept all URLs
        if not self.page_keywords:
            return True
        
        # Check if any keyword is found in the URL
        url_lower = url.lower()
        for keyword in self.page_keywords:
            if keyword.lower() in url_lower:
                return True
        
        return False
        


    # Primary method to crawl the web starting from the base URL
    def crawl(self, base_url, max_depth=MAX_DEPTH):

        logger.info(f"Starting crawl from: {base_url}") # Initialize the stack with the base URL and depth
        urls_to_visit = [(base_url, 0)] # (url, depth)

        # Start a thread to monitor user input for stopping the crawler
        self.start_input_monitor()
    

        # Loop through the URLs to visit
        with tqdm(desc="Crawling pages", unit="pages", dynamic_ncols=True,
                  mininterval=0.1, maxinterval=1.0) as pbar:
            
            start_time = time.time()
            

            # Setting the thread for the timer
            def update_timer():
                while not self.stop_crawling:
                    elapsed = time.time() - start_time
    
                    # Mantain the description but update timer
                    postfix_data= {
                        'visited' : len(self.visited_urls),
                        'found' : len(self.found_links),
                        'queue': len(urls_to_visit),
                    }
                    pbar.set_postfix(**postfix_data)
                    pbar.refresh()
                    time.sleep(1)
            
            #Start the thread
            timer_thread = threading.Thread(target=update_timer, daemon=True)
            timer_thread.start()


            while urls_to_visit and not self.stop_crawling:
                current_url, depth = urls_to_visit.pop(0)

                #check if the URL has already been visited
                if current_url in self.visited_urls:
                    # Logic for progress bar
                    pbar.set_description(f"Crawling (skipping visited): {urlparse(current_url).path[:30]}")
                    #----------------------------------

                    continue
        
                # Check if the maximum depth has been reached
                if depth > max_depth:
                    # Logic for progress bar
                    pbar.set_description(f"Crawling (max depth reached)")
                    #-----------------------------------

                    continue
                        

                # Mark the URL as visited
                self.visited_urls.add(current_url)

                # Get the page content
                soup = self.get_page(current_url)
                if soup is None:
                    continue
                    
                pbar.set_description(f"Extracting links: {urlparse(current_url).path[:20]}")

                # Extract links from the page content
                links = self.extract_links(soup, current_url)

                # logic for progress bar
                pbar.set_description(f"Processed: {urlparse(current_url).path[:25]}")
                pbar.update(1) # Increment only if a new page is processed
                #-----------------------------------

                for link in links:
                    if link not in self.visited_urls:
                        urls_to_visit.append((link, depth + 1))
                        self.crawl_path[link] = current_url # Track the path: remember where this link came from


            # Final progress bar logic
            elapsed = time.time() - start_time
            pbar.set_description("Crawling completed")
            pbar.set_postfix(visited=len(self.visited_urls), 
                        found=len(self.found_links), 
                        total_time=f"{elapsed:.1f}s")
            #-----------------------------------



        # Log crawling statistics
        logger.info(f"Crawling statistics:")
        logger.info(f"- Total URLs visited: {len(self.visited_urls)}")
        logger.info(f"- Total links found: {len(self.found_links)}")
        logger.info(f"- Max depth reached: {max_depth}")
        logger.info(f"- Base domain: {urlparse(self.base_url).netloc}")
        if self.page_keywords:
            logger.info(f"- Page keywords used: {', '.join(self.page_keywords)}")