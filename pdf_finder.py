# Uses the crawler to find and download PDF files from a website.

import requests
import os
from urllib.parse import urlparse
from crawler import WebCrawler
from config import DOWNLOAD_FOLDER, MAX_FILE_SIZE, USER_AGENT, DELAY_BETWEEN_REQUESTS
import time
import re
from tqdm import tqdm
import threading


import logging
logger = logging.getLogger('downloader')  # Initialize a logger for the downloader

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

        # Log the statistics of the found links
        total_links = len(self.crawler.found_links)
        pdf_links_found = len([link for link in self.crawler.found_links if self.is_pdf_link(link)])
        pdf_links_after_keywords = len(pdf_links)

        logger.debug(f"Link analysis:")
        logger.debug(f"- Total links found: {total_links}")
        logger.debug(f"- PDF links detected: {pdf_links_found}")
        logger.debug(f"- PDF links after keyword filtering: {pdf_links_after_keywords}")
        
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


    # Sanitize the domain name to create a valid filename
    def _sanitize_domain_name(self, domain):
        
        # Remove protocol if present
        domain = domain.replace('http://', '').replace('https://', '')
        # Remove www. prefix if present
        domain = domain.replace('www.', '')
        # Remove port if present
        domain = domain.split(':')[0]
        # Replace invalid filename characters with underscores
        domain = re.sub(r'[<>:"/\\|?*]', '_', domain)
        # Replace dots with underscores except for the last one
        parts = domain.split('.')
        if len(parts) > 1:
            domain = '_'.join(parts[:-1]) + '.' + parts[-1]
        return domain




    # Download the PDF file
    def download_pdf(self, url, filename=None):

        try:
            logger.info(f"Downloading PDF from: {url}")

            # If no filename is provided, use the last part of the URL
            if filename is None:
                parsed_url = urlparse(url)
                domain = self._sanitize_domain_name(parsed_url.netloc)
                
                # Try to get original filename
                original_filename = os.path.basename(parsed_url.path)
                if original_filename and original_filename.endswith('.pdf'):
                    # Remove .pdf extension temporarily
                    base_name = original_filename[:-4]
                    # Clean the base name
                    base_name = re.sub(r'[<>:"/\\|?*]', '_', base_name)
                    filename = f"{domain}_{base_name}.pdf"
                else:
                    # Generate unique filename with domain
                    unique_id = hash(url) % 10000
                    # Complete the filename with the download folder
                    filename = f"{domain}_{unique_id}.pdf"

            filepath = os.path.join(DOWNLOAD_FOLDER, filename)

            # Check if the file already exists
            if os.path.exists(filepath):
                logger.debug(f"File already exists, skipping: {filename}.")
                return filepath

            # Download the PDF file
            response = self.session.get(url, 
                                  timeout=30,           # Timeout più lungo
                                  allow_redirects=True, # Gestisce redirect
                                  stream=True)          # Per file grandi
            
            response.raise_for_status()  # Raise an error for bad responses

            # Check content type to verify it's actually a PDF
            content_type = response.headers.get('Content-Type', '').lower()
            if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                logger.warning(f"Warning: Content type is '{content_type}', may not be a PDF")

            # Check file size before downloading
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > MAX_FILE_SIZE:
                logger.warning(f"File too large ({content_length} bytes > {MAX_FILE_SIZE} bytes). Skipping.")
                return None



            # Save the PDF file
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive chunks
                        file.write(chunk)

            logger.info(f"Downloaded {filename} to {DOWNLOAD_FOLDER}")
            time.sleep(DELAY_BETWEEN_REQUESTS)  # Delay between requests to avoid overloading the server
            return filepath
        
        except requests.exceptions.ConnectionError as e:
            if "Failed to resolve" in str(e) or "getaddrinfo failed" in str(e):
                logger.error(f"DNS resolution error for {url}. Check internet connection or try again later.")
            else:
                logger.error(f"Connection error downloading {url}: {e}")
            return None
        except requests.exceptions.Timeout:
            logger.error(f"Timeout error downloading {url}. Server may be slow or unresponsive.")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error downloading {url}: Status code {e.response.status_code}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error downloading {url}: {e}")
            return None
        except OSError as e:
            logger.error(f"File system error saving {filename}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading {url}: {e}")
            return None



    # Main method to find and download PDFs
    def run(self, max_downloads=None):  # Nessun limite di default

        logger.info(f"Starting PDF search on {self.base_url}")
        logger.info(f"Base domain: {urlparse(self.base_url).netloc}")
        if self.pdf_keywords:
            logger.info(f"Filtering PDFs with keywords: {', '.join(self.pdf_keywords)}")
        else:
            logger.info("No PDF keywords filter - downloading all PDFs found")


        # Find PDF links on the website
        pdf_links = self.find_pdf_links()

        if not pdf_links:
            logger.debug("No PDF links found.")
            return []
        
        # Download all found PDF files
        downloaded_files = []
        logger.info(f"Downloading {len(pdf_links)} PDF files...")

        # Create a progress bar for the download process
        with tqdm(total=len(pdf_links), desc="Downloading PDFs", unit="file",
                  dynamic_ncols=True, mininterval=0.1, maxinterval=1.0,
                  bar_format='{l_bar}{bar} | {n_fmt}/{total_fmt} [{elapsed}<{remaining},{postfix}]') as pbar:

            start_time = time.time()  # Start the timer

            # Thread per aggiore il timer automaticamente
            def update_download_timer():

                estimated_total_time = None

                while len(downloaded_files) + failed_downloads < len(pdf_links):
                    elapsed = time.time() - start_time
                    success_count = len(downloaded_files )

                    # Calculate estimated total time if not already set
                    if success_count > 0 and estimated_total_time is None:
                        avg_time_per_file = elapsed / success_count
                        estimated_total_time = avg_time_per_file * (len(pdf_links) + 1)

                    # Calcola tempo rimanente manualmente
                    if estimated_total_time:
                        remaining_time = max(0, estimated_total_time)
                        
                        pbar.set_postfix(
                            success=success_count,
                            failed=failed_downloads,
                            remaining=f"{remaining_time:.0f}s"  # Mostrato nei postfix
                        )
                    else:
                        pbar.set_postfix(
                            success=success_count,
                            failed=failed_downloads
                        )

                    pbar.refresh()
                    time.sleep(1)

            failed_downloads = 0
            timer_thread = threading.Thread(target=update_download_timer, daemon = True)
            timer_thread.start()



            # Loop through the found PDF links and download them
            for i, pdf_url in enumerate(pdf_links,1):

                # Check if the URL is valid
                filename_from_url = os.path.basename(pdf_url)
                if filename_from_url:
                    # Decode URL-encoded characters
                    import urllib.parse
                    filename_from_url = urllib.parse.unquote(filename_from_url)
                    # Parse the filename to remove unwanted characters
                    filename_from_url = re.sub(r'[O__O]+', '_', filename_from_url)
                    filename_from_url = filename_from_url.replace('+', '_')
                    # Cut the filename to a maximum length
                    filename_display = filename_from_url[-25:]
                else:
                    filename_display = f"file_{i}.pdf"


                pbar.set_description(f"[{i}/{len(pdf_links)}] Downloading {filename_display}")
                logger.info(f"\n[{i}/{len(pdf_links)}] Downloading: {pdf_url}")

                filepath = self.download_pdf(pdf_url)

                if filepath:
                    downloaded_files.append(filepath)
                else:
                    failed_downloads += 1
                    pbar.set_description(f"Failed {filename_display}")
                    logger.error(f"Failed to download {pdf_url}")
    
                # Update progress bar
                pbar.update(1)


        # Final progress bar logic
        elapsed = time.time() - start_time
        pbar.set_description("Downloads completed")
        pbar.set_postfix(
            success=len(downloaded_files),
            failed=failed_downloads,
            total_time=f"{elapsed:.1f}s"
        )

        # Log the download summary
        success_rate = (len(downloaded_files) / len(pdf_links)) * 100 if pdf_links else 0
        logger.info(f"Download summary:")
        logger.info(f"- Total PDF links found: {len(pdf_links)}")
        logger.info(f"- Successfully downloaded: {len(downloaded_files)}")
        logger.info(f"- Success rate: {success_rate:.1f}%")
        logger.info(f"- Download folder: {DOWNLOAD_FOLDER}")
        
        
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
    


