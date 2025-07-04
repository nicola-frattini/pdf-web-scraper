from config import MAX_DEPTH
from pdf_finder import PDFFinder
import sys
import os

def main():
        
    os.system('cls')
    print("=== PDF Web Scraper ===")

    #Aske the user for the base URL
    base_url = input("Enter the base URL to scrape for PDFs: ").strip()

    if not base_url:
        print("Base not valid. Exiting.")
        return
    
    # Add keywords if needed
    if not base_url.startswith(('http://', 'https://')):
        base_url = 'http://' + base_url

    # Ask for keywords
    pdf_keywords_input = input("Enter keywords to filter PDFs (comma separated, leave empty for no filtering): ").strip()
    page_keywords_input = input("Enter keywords to filter pages to visit (comma separated, leave empty for no filtering): ").strip()

    pdf_keywords = []
    if pdf_keywords_input:
        pdf_keywords = [k.strip() for k in pdf_keywords_input.split(',') if k.strip()]

    page_keywords = []
    if page_keywords_input:
        page_keywords = [k.strip() for k in page_keywords_input.split(',') if k.strip()]

    print(f"\nConfiguration:")
    print(f"Base URL: {base_url}")
    print(f"PDF Keywords: {pdf_keywords if pdf_keywords else 'None'}")
    print(f"Page Keywords: {page_keywords if page_keywords else 'None'}")
    print(f"Max Depth: {MAX_DEPTH}")

    confirm = input("Do you want to proceed? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Exiting.")
        return
    
    # Initialize the PDF finder
    try:
        finder = PDFFinder(base_url, pdf_keywords, page_keywords)
        downloaded_files = finder.run()

        print(f"\nFound and downloaded {len(downloaded_files)} PDF files:")
        
        if downloaded_files:
            print(f"Files saved in: downloaded_pdfs")
            print(f"Downloaded files:")
            for file in downloaded_files:
                print(f"- {file}")
        else:
            print("No PDF files found.")


    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

    
