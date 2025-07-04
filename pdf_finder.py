# Uses the crawler to find and download PDF files from a website.

import requests
import os
from urllib.parse import urlparse
from crawler import WebCrawler
from config import DOWNLOAD_FOLDER, MAX_FILE_SIZE, USER_AGENT, DELAY_BETWEEN_REQUESTS
import time


class PDFFinder:

    # PDFFinder initialization
    def __init__(self,base_url, pdf_keywords=None, page_keywords=None):
        self.base_url = base_url # Base URL to start crawling
        self.pdf_keywords = pdf_keywords or [] # List of keywords to filter PDF files
        self.crawler = WebCrawler(base_url,page_keywords= page_keywords or []) # Initialize the WebCrawler with the base URL
        self.session = requests.Session() # Initialize a session for making requests
        self.session.headers.update({'User-Agent': USER_AGENT}) # Initialize session with user agent

        # Create the download folder if it doesn't exist
        if not os.path.exists(DOWNLOAD_FOLDER):
            os.makedirs(DOWNLOAD_FOLDER)

    # Find PDF links on the website
    def find_pdf_links(self):
    
        # Execute the crawler to find links
        self.crawler.crawl(self.base_url)

        # Filter the found links to only include PDF links
        pdf_links = []
        for link in self.crawler.found_links:
            if self.is_pdf_link(link):
                # Check if the link contains any of the keywords
                if not self.pdf_keywords or self.matches_keywords(link):
                    pdf_links.append(link)

        print(f"Found {len(pdf_links)} PDF links.")
        return pdf_links


    # Verify if the URL is a valid PDF link
    def is_pdf_link(self, url):
        
        # Check if the URL ends with .pdf
        if url.lower().endswith('.pdf'):
            return True
        
        # Check if the URL contains the correct content type
        url_lower = url.lower()
        pdf_indicators = ['/pdf/', '.pdf?', 'pdf=', 'format=pdf', 'type=pdf']
        if any(indicator in url_lower for indicator in pdf_indicators):
            return True
        
        return False


    # Download the PDF file
    def download_pdf(self, url, filename=None):

        try:
            print(f"Downloading PDF from: {url}")

            # If no filename is provided, use the last part of the URL
            if filename is None:
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename or not filename.endswith('.pdf'):
                    filename = f"document_{hash(url) % 10000}.pdf"  # Generate a unique filename if the URL doesn't provide one

            # Complete the filename with the download folder
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)

            # Check if the file already exists
            if os.path.exists(filepath):
                print(f"File {filename} already exists. Skipping download.")
                return filepath

            # Download the PDF file
            response = self.session.get(url, timeout=10)
            response.raise_for_status()  # Raise an error for bad responses

            # Save the PDF file
            with open(filepath, 'wb') as file:
                file.write(response.content)

            print(f"Downloaded {filename} to {DOWNLOAD_FOLDER}")
            time.sleep(DELAY_BETWEEN_REQUESTS)  # Delay between requests to avoid overloading the server
            return filepath
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return None




    # Main method to find and download PDFs
    def run(self, max_downloads=None):  # Nessun limite di default

        print(f"Starting PDF search on {self.base_url}...")
        if self.pdf_keywords:
            print(f"Filtering PDFs with keywords: {', '.join(self.pdf_keywords)}")

        # Find PDF links on the website
        pdf_links = self.find_pdf_links()

        if not pdf_links:
            print("No PDF links found.")
            return []
        
        # Download all found PDF files
        downloaded_files = []
        print(f"Downloading {len(pdf_links)} PDF files...")

        # Loop through the found PDF links and download them
        for i, pdf_url in enumerate(pdf_links,1):
            print(f"\n[{i}/{len(pdf_links)}]", end = " ")
            filepath = self.download_pdf(pdf_url)
            if filepath:
                downloaded_files.append(filepath)
            else:
                print(f"Failed to download {pdf_url}")
    
        print(f"\nDownloaded {len(downloaded_files)} PDF files.")
        return downloaded_files


    
    # Check if the URL or filename matches any of the specified keywords
    def matches_keywords(self, url):
        
        if not self.pdf_keywords:
            return True # If no keywords are specified, accept all URLs
        
        url_lower = url.lower()
        for keyword in self.pdf_keywords:
            if keyword.lower() in url_lower:
                return True
        return False
    


