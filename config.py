# Configurazioni per il PDF scraper

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
DELAY_BETWEEN_REQUESTS = 10  # 10 secondi come richiesto da robots.txt comune.verona.it
MAX_DEPTH = 2  # profondità massima di crawling
DOWNLOAD_FOLDER = "downloaded_pdfs"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max per PDF