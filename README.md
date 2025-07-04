# 📄 PDF Web Scraper

Un potente strumento Python per trovare e scaricare file PDF da siti web in modo automatico e intelligente.

## 🚀 Caratteristiche

- 🔍 **Crawling intelligente** - Esplora automaticamente tutte le pagine del sito
- 🎯 **Filtro contenuti** - Analizza solo le aree di contenuto principale, evitando menu e footer
- 📋 **Filtri personalizzabili** - Cerca PDF con parole chiave specifiche
- ⏹️ **Controllo manuale** - Interrompi il crawling in qualsiasi momento premendo ENTER
- 📁 **Download automatico** - Scarica tutti i PDF trovati in una cartella dedicata
- 🛡️ **Rispettoso dei server** - Include delay configurabili tra le richieste
- 🧭 **Tracciamento percorso** - Mostra da dove proviene ogni link visitato
- 🏗️ **Architettura modulare** - Codice ben organizzato e facilmente estendibile
- ⚡ **Gestione errori robusta** - Continua a funzionare anche con link non funzionanti
- 🌐 **Rispetto del dominio** - Rimane sempre sullo stesso dominio di partenza

## 📦 Installazione

### Prerequisiti
- Python 3.7+
- pip

### Installa le dipendenze
```bash
pip install -r requirements.txt
```

**Oppure manualmente:**
```bash
pip install requests beautifulsoup4 lxml urllib3
```

### Installazione con ambiente virtuale (consigliato)
```bash
# Crea ambiente virtuale
python -m venv pdf_scraper_env

# Attiva ambiente virtuale (Windows)
pdf_scraper_env\Scripts\activate

# Installa dipendenze
pip install -r requirements.txt
```

## 📂 Struttura del progetto

```
Scraping/
├── config.py           # Configurazioni globali
├── crawler.py          # Motore di crawling del sito
├── pdf_finder.py       # Ricerca e download dei PDF
├── scrape.py           # Script principale
├── requirements.txt    # Dipendenze del progetto
├── README.md           # Questa documentazione
└── downloaded_pdfs/    # Cartella dei PDF scaricati (creata automaticamente)
```

## 🎯 Utilizzo

### Utilizzo Interattivo
```bash
python scrape.py
```

Il programma ti chiederà:
1. **URL del sito** da esplorare
2. **Parole chiave** per filtrare i PDF (opzionale)
3. **Conferma** prima di iniziare

### Test rapido con siti sicuri
```bash
# Siti di test consigliati:
# - http://quotes.toscrape.com
# - https://books.toscrape.com  
# - https://www.python.org (con keywords: tutorial, guide, documentation)
# - https://sabbio.etrasparenza.it (per testare PDF governativi)
```

### ⏹️ Interruzione Manuale
Durante il crawling, puoi interrompere il processo in qualsiasi momento:
- **Premi ENTER** per fermare il crawling
- Il sistema completerà la richiesta corrente e scaricherà i PDF trovati fino a quel momento
- Non perdere nessun PDF già individuato!

### Esempio di sessione
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

# Premendo ENTER durante il crawling:
Stopping crawling... will finish current requests.
Crawling completed. Found 5 links.
Visited 3 URLs.

Downloading 5 PDF files...
[1/5] Downloaded user_manual.pdf to downloaded_pdfs
[2/5] Downloaded installation_guide.pdf to downloaded_pdfs
...
Downloaded 5 PDF files.
```

### Utilizzo Programmatico

```python
from pdf_finder import PDFFinder

# Cerca PDF con parole chiave
finder = PDFFinder("https://www.example.com", keywords=["manual", "guide"])
downloaded_files = finder.run()

print(f"Scaricati {len(downloaded_files)} file PDF")
```

## ⚙️ Configurazione

Modifica il file `config.py` per personalizzare il comportamento:

```python
# Configurazioni per il PDF scraper
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
DELAY_BETWEEN_REQUESTS = 1  # secondi tra le richieste
MAX_DEPTH = 2  # profondità massima di crawling (aumentata per crawling più efficace)
DOWNLOAD_FOLDER = "downloaded_pdfs"  # cartella di download
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max per PDF
```

## 🎯 Funzionalità Avanzate

### 🔍 Crawling Intelligente
Il sistema utilizza un approccio intelligente per il crawling:

- **Filtraggio delle aree di contenuto**: Cerca link solo nelle aree principali (`main`, `article`, `.content`, ecc.)
- **Esclusione della navigazione**: Evita menu, header, footer e link di navigazione
- **Tracciamento del percorso**: Mostra da dove proviene ogni URL visitato
- **Fallback automatico**: Se non trova aree di contenuto, usa tutti i link escludendo la navigazione

### ⏹️ Controllo Interattivo
- **Interruzione manuale**: Premi ENTER in qualsiasi momento per fermare il crawling
- **Thread separato**: Il monitoraggio dell'input non interferisce con il crawling
- **Completamento sicuro**: Finisce le richieste in corso prima di fermarsi
- **Download garantito**: Tutti i PDF trovati vengono scaricati anche dopo l'interruzione

## 🔧 Parametri Avanzati

### WebCrawler
- **base_url**: URL di partenza per il crawling
- **max_depth**: Profondità massima di navigazione (default: 2)
- **page_keywords**: Parole chiave per filtrare le pagine (attualmente disabilitato)
- **stop_crawling**: Flag per interruzione manuale

### PDFFinder
- **base_url**: URL del sito da esplorare
- **keywords**: Lista di parole chiave per filtrare i PDF
- **download_folder**: Cartella di destinazione per i download
- **pdf_keywords**: Filtri specifici per i PDF (separati dai filtri delle pagine)

## 🛡️ Considerazioni Etiche e Legali

⚠️ **IMPORTANTE**: Utilizza questo strumento in modo responsabile!

### ✅ Buone Pratiche
- Controlla sempre il file `robots.txt` del sito
- Leggi i Terms of Service prima di fare scraping
- Usa delay appropriati tra le richieste
- Non sovraccaricare i server
- Rispetta i diritti d'autore dei documenti

### 🎯 Siti Consigliati per Test
- `http://quotes.toscrape.com` - Sito di test
- `https://books.toscrape.com` - Libreria di test
- Siti educativi e universitari pubblici
- Il tuo sito web personale

### ❌ Evita
- Siti con dati sensibili o personali
- Siti che esplicitamente vietano il crawling
- Rate limiting aggressivo
- Download di contenuti protetti da copyright

## 🐛 Risoluzione Problemi

### Errori Comuni

**"urlunparse() takes 1 positional argument but 6 were given"**
```python
# ❌ Sbagliato
clean_url = urlunparse(scheme, netloc, path, params, query, fragment)

# ✅ Corretto  
clean_url = urlunparse((scheme, netloc, path, params, query, fragment))
```

**"No PDF files found"**
- Controlla che il sito contenga effettivamente PDF
- Prova senza parole chiave per vedere tutti i link
- Verifica che l'URL sia corretto
- Alcuni PDF potrebbero essere dietro form o login
- Aumenta MAX_DEPTH se i PDF sono in pagine più profonde

**Crawling che si ferma troppo presto**
- Verifica che il sito non usi JavaScript per caricare i contenuti
- Controlla se ci sono aree di contenuto riconosciute dal sistema
- Guarda i messaggi "DEBUG - Found content area" nell'output

**"DEBUG - No content area found, using all links"**
- Il sito non usa tag semantici standard
- Il sistema userà tutti i link escludendo la navigazione
- Questo è normale per siti più vecchi o con struttura non standard

**Timeout o errori di connessione**
- Controlla la connessione internet
- Aumenta il timeout in `config.py`
- Alcuni siti potrebbero bloccare i bot

## 📊 Output

I PDF scaricati vengono salvati nella cartella `downloaded_pdfs/` con:
- **Nome originale** quando possibile
- **Nome generato** per URL senza estensione chiara
- **Controllo duplicati** - non scarica file già esistenti
- **Log dettagliato** di tutte le operazioni
- **Tracciamento percorso** - mostra da dove proviene ogni link visitato
- **Debug delle aree di contenuto** - indica quali aree HTML sono state analizzate

### Esempio di Output Dettagliato
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

## 🔄 Estensioni Future

- [ ] Supporto per autenticazione (login)
- [ ] Crawling multi-thread per velocità
- [ ] Filtri per dimensione e tipo di file
- [ ] Interfaccia grafica (GUI)
- [ ] Supporto per proxy e VPN
- [ ] Database dei file scaricati
- [ ] Scheduling automatico
- [ ] Supporto per altri formati (DOCX, XLSX, etc.)
- [ ] Analisi del contenuto dei PDF scaricati
- [ ] Supporto per JavaScript-rendered content
- [ ] Configurazione avanzata delle aree di contenuto
- [ ] Ripresa del crawling da dove si era interrotto
- [ ] Statistiche dettagliate del crawling

## 📝 File di Configurazione

Il progetto include un file `requirements.txt` aggiornato per semplificare l'installazione:

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

## 🔍 File del Progetto

### `config.py`
Contiene tutte le configurazioni globali del sistema.

### `crawler.py`  
Implementa la classe `WebCrawler` per esplorare i siti web con:
- Crawling intelligente delle aree di contenuto
- Sistema di interruzione manuale tramite thread separato
- Tracciamento del percorso per debug
- Filtraggio automatico di menu e navigazione

### `pdf_finder.py`
Implementa la classe `PDFFinder` per cercare e scaricare PDF con:
- Integrazione con WebCrawler per il filtraggio intelligente
- Download con gestione errori robusta
- Filtri per parole chiave nei nomi dei PDF

### `scrape.py`
Script principale con interfaccia utente interattiva.

## 🤝 Contribuire

1. Fork del repository
2. Crea un feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file `LICENSE` per maggiori dettagli.

## ✨ Autore

Creato con ❤️ per semplificare la ricerca e il download di documenti PDF dal web.

---

⭐ Se questo progetto ti è stato utile, lascia una stella!
