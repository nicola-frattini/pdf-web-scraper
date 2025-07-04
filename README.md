# PDF Web Scraper

A powerful Python tool for automatically finding and downloading PDF files from websites with intelligent crawling capabilities.

## Features

- **Intelligent Crawling** - Automatically explores all pages of the website
- **Content Filtering** - Analyzes only main content areas, avoiding menus and footers
- **Customizable Filters** - Search for PDFs with specific keywords
- **Manual Control** - Stop crawling at any time by pressing ENTER
- **Automatic Download** - Downloads all found PDFs to a dedicated folder
- **Server Respectful** - Includes configurable delays between requests
- **Path Tracking** - Shows where each visited link comes from
- **Modular Architecture** - Well-organized and easily extensible code
- **Robust Error Handling** - Continues working even with broken links
- **Domain Respect** - Always stays within the same starting domain

## Installation

### Prerequisites
- Python 3.7+
- pip

### Install Dependencies
```bash
pip install -r requirements.txt
```

**Or manually:**
```bash
pip install requests beautifulsoup4 lxml urllib3
```

### Installation with Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv pdf_scraper_env

# Activate virtual environment (Windows)
pdf_scraper_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Project Structure

```
Scraping/
├── config.py           # Global configurations
├── crawler.py          # Website crawling engine
├── pdf_finder.py       # PDF search and download
├── scrape.py           # Main script
├── requirements.txt    # Project dependencies
├── README.md           # This documentation
└── downloaded_pdfs/    # Downloaded PDFs folder (created automatically)
```

## Usage

### Interactive Usage
```bash
python scrape.py
```

The program will ask you for:
1. **Website URL** to explore
2. **Keywords** to filter PDFs (optional)
3. **Confirmation** before starting

### Quick Test with Safe Sites
```bash
# Recommended test sites:
# - http://quotes.toscrape.com
# - https://books.toscrape.com  
# - https://www.python.org (with keywords: tutorial, guide, documentation)
# - https://sabbio.etrasparenza.it (for testing government PDFs)
```

### Manual Interruption
During crawling, you can interrupt the process at any time:
- **Press ENTER** to stop crawling
- The system will complete the current request and download PDFs found up to that point
- You won't lose any PDFs already discovered!

### Example Session
```
=== PDF Web Scraper ===
Enter the base URL to scrape for PDFs: https://www.example.com
Enter keywords to filter PDFs (comma separated, leave empty for no filtering): manual, guide, tutorial

Configuration:
Base URL: https://www.example.com
PDF Keywords: ['manual', 'guide', 'tutorial']
Max Depth: 2
Do you want to proceed? (y/n): y

Starting PDF search on https://www.example.com...
Filtering PDFs with keywords: manual, guide, tutorial
Starting crawl from: https://www.example.com
Press Enter to stop crawling...

Visiting: https://www.example.com → (starting point)
DEBUG - Found content area: main
Visiting: https://www.example.com/docs → (from https://www.example.com)
Visiting: https://www.example.com/support → (from https://www.example.com)
Found 5 PDF links.

# Pressing ENTER during crawling:
Stopping crawling... will finish current requests.
Crawling completed. Found 5 links.
Visited 3 URLs.

Downloading 5 PDF files...
[1/5] Downloaded user_manual.pdf to downloaded_pdfs
[2/5] Downloaded installation_guide.pdf to downloaded_pdfs
...
Downloaded 5 PDF files.
```

### Programmatic Usage

```python
from pdf_finder import PDFFinder

# Search for PDFs with keywords
finder = PDFFinder("https://www.example.com", keywords=["manual", "guide"])
downloaded_files = finder.run()

print(f"Downloaded {len(downloaded_files)} PDF files")
```

## Configuration

Edit the `config.py` file to customize behavior:

```python
# Configurations for PDF scraper
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
DELAY_BETWEEN_REQUESTS = 1  # seconds between requests
MAX_DEPTH = 2  # maximum crawling depth (increased for more effective crawling)
DOWNLOAD_FOLDER = "downloaded_pdfs"  # download folder
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max per PDF
```

## Advanced Features

### Intelligent Crawling
The system uses an intelligent approach for crawling:

- **Content area filtering**: Searches for links only in main areas (`main`, `article`, `.content`, etc.)
- **Navigation exclusion**: Avoids menus, headers, footers, and navigation links
- **Path tracking**: Shows where each visited URL comes from
- **Automatic fallback**: If no content areas are found, uses all links excluding navigation

### Interactive Control
- **Manual interruption**: Press ENTER at any time to stop crawling
- **Separate thread**: Input monitoring doesn't interfere with crawling
- **Safe completion**: Finishes current requests before stopping
- **Guaranteed download**: All found PDFs are downloaded even after interruption

## Advanced Parameters

### WebCrawler
- **base_url**: Starting URL for crawling
- **max_depth**: Maximum navigation depth (default: 2)
- **page_keywords**: Keywords to filter pages (currently disabled)
- **stop_crawling**: Flag for manual interruption

### PDFFinder
- **base_url**: Website URL to explore
- **keywords**: List of keywords to filter PDFs
- **download_folder**: Destination folder for downloads
- **pdf_keywords**: Specific filters for PDFs (separate from page filters)

## Ethical and Legal Considerations

**IMPORTANT**: Use this tool responsibly!

### Best Practices
- Always check the website's `robots.txt` file
- Read Terms of Service before scraping
- Use appropriate delays between requests
- Don't overload servers
- Respect document copyrights

### Recommended Test Sites
- `http://quotes.toscrape.com` - Test site
- `https://books.toscrape.com` - Test bookstore
- Public educational and university sites
- Your personal website

### Avoid
- Sites with sensitive or personal data
- Sites that explicitly prohibit crawling
- Aggressive rate limiting
- Downloading copyright-protected content

## Troubleshooting

### Common Errors

**"urlunparse() takes 1 positional argument but 6 were given"**
```python
# Wrong
clean_url = urlunparse(scheme, netloc, path, params, query, fragment)

# Correct  
clean_url = urlunparse((scheme, netloc, path, params, query, fragment))
```

**"No PDF files found"**
- Check that the site actually contains PDFs
- Try without keywords to see all links
- Verify that the URL is correct
- Some PDFs might be behind forms or login
- Increase MAX_DEPTH if PDFs are in deeper pages

**Crawling stops too early**
- Check if the site uses JavaScript to load content
- Verify if there are content areas recognized by the system
- Look for "DEBUG - Found content area" messages in output

**"DEBUG - No content area found, using all links"**
- The site doesn't use standard semantic tags
- The system will use all links excluding navigation
- This is normal for older sites or non-standard structure

**Timeout or connection errors**
- Check internet connection
- Increase timeout in `config.py`
- Some sites might block bots

## Output

Downloaded PDFs are saved in the `downloaded_pdfs/` folder with:
- **Original name** when possible
- **Generated name** for URLs without clear extension
- **Duplicate check** - doesn't download existing files
- **Detailed logging** of all operations
- **Path tracking** - shows where each visited link comes from
- **Content area debugging** - indicates which HTML areas were analyzed

### Detailed Output Example
```
Starting crawl from: https://example.com
Press Enter to stop crawling...

Visiting: https://example.com → (starting point)
DEBUG - Found content area: main
Visiting: https://example.com/docs → (from https://example.com)
DEBUG - Found content area: article
Visiting: https://example.com/downloads → (from https://example.com/docs)
DEBUG - No content area found, using all links

Crawling completed. Found 15 links.
Visited 8 URLs.
Found 3 PDF links.
Downloading 3 PDF files...
```

## Future Extensions

- [ ] Multi-threaded crawling for speed
- [ ] Filters for file size and type
- [ ] Graphical User Interface (GUI)
- [ ] Support for proxy and VPN
- [ ] Downloaded files database
- [ ] Automatic scheduling
- [ ] Support for other formats (DOCX, XLSX, etc.)
- [ ] Downloaded PDF content analysis
- [ ] Support for JavaScript-rendered content
- [ ] Advanced content area configuration
- [ ] Resume crawling from where it stopped
- [ ] Detailed crawling statistics

## Configuration Files

The project includes an updated `requirements.txt` file to simplify installation:

```
# Web scraping dependencies
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0

# Additional HTTP libraries (used by requests)
urllib3>=2.0.0,<3.0.0
certifi>=2023.7.22

# Optional: for better SSL support
requests[security]>=2.31.0
```

## Project Files

### `config.py`
Contains all global system configurations.

### `crawler.py`  
Implements the `WebCrawler` class for website exploration with:
- Intelligent crawling of content areas
- Manual interruption system via separate thread
- Path tracking for debugging
- Automatic filtering of menus and navigation

### `pdf_finder.py`
Implements the `PDFFinder` class for searching and downloading PDFs with:
- Integration with WebCrawler for intelligent filtering
- Download with robust error handling
- Keyword filters for PDF names

### `scrape.py`
Main script with interactive user interface.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is released under the MIT license. See the `LICENSE` file for more details.

## Author

Created with care to simplify PDF document search and download from the web.

---

If this project was useful to you, please give it a star!
