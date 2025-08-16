# 🍺 Beerizer Beer Scraper & AI Label Analysis

This project scrapes beers from [beerizer.com](https://beerizer.com), analyzes each beer label image with LLaVA (via Ollama), and saves results in batches and a master CSV.  
**If interrupted, the script will resume from the next incomplete batch.**

---

## Features

- **Scrapes all beers from Beerizer (1676 pages)**
- **Downloads, analyzes, and deletes each beer image one at a time**
- **Saves every 100 pages to a separate CSV** (`beers_1_100.csv`, `beers_101_200.csv`, ...)
- **Appends all results to a master CSV** (`beers_all.csv`)
- **Skips already completed batches for safe resuming**
- **Only includes beers with a valid rating**
- **LLaVA, Ollama, and ChatGPT analysis options**

---

## Requirements

- Python 3.8+
- [Ollama](https://ollama.com/) running locally with a LLaVA model pulled (e.g. `llava:7b`)
- Python packages: `requests`, `beautifulsoup4`, `pandas` (for LLaVA analysis)

Install dependencies:
```sh
pip install requests beautifulsoup4 pandas
```

---

## Usage

### 1. Start Ollama and Pull LLaVA Model

```sh
ollama serve
ollama pull llava:7b
```

### 2. Run the Scraper & Analyzer

```sh
python scrape_and_analyze.py
```

- This will scrape all beers, analyze each image, and save results in batches and a master CSV.
- If interrupted, just run the script again. It will skip batches that are already saved.

---

## Output

- **Batch CSVs:** `beers_1_100.csv`, `beers_101_200.csv`, ...  
  Each contains all beers scraped and analyzed in that batch.
- **Master CSV:** `beers_all.csv`  
  Contains all beers from all batches.
- **Images:** Downloaded and deleted one-by-one during processing.

---

## Advanced: AI Analysis Options

This project supports three AI analysis methods:

### 1. **LLaVA Analysis** (Recommended for Images)
- Uses LLaVA vision models via Ollama
- Can directly see and analyze beer label images
- No API costs, runs completely offline
- Provides the richest visual analysis
- Files: `llava_analysis.py`, `scrape_and_analyze.py`

### 2. **Ollama Analysis** (Text-only)
- Uses local AI models via Ollama
- No API costs, runs completely offline
- Files: `ollama_analysis.py`, `setup_ollama_analysis.py`

### 3. **ChatGPT Analysis** (Cloud-based)
- Uses OpenAI's GPT models via API
- Requires OpenAI API key and internet connection
- Costs money per analysis
- Files: `chatgpt_analysis.py`, `setup_chatgpt_analysis.py`

---

## Troubleshooting

- **LLaVA/Ollama not found:**  
  Make sure Ollama is running and the LLaVA model is pulled.
- **Selectors not working:**  
  Inspect the Beerizer website and update the selectors in the script if needed.
- **Partial batches:**  
  The script will skip any batch CSV that already exists. To re-run a batch, delete its CSV file.

---

## File Structure

```
beer project/
├── scrape_and_analyze.py      # Scraper and analyzer with batching and resume
├── llava_analysis.py          # LLaVA vision analysis functions
├── ollama_analysis.py         # Ollama text-only analysis
├── chatgpt_analysis.py        # ChatGPT integration
├── requirements.txt           # Dependencies
├── beers_all.csv              # Master CSV (all beers)
├── beers_1_100.csv            # Example batch CSV
├── beer_images/               # Beer label images (temporary)
└── ... (other scripts and outputs)
```

---

## License

MIT

---

**Tip:**  
If Beerizer changes their HTML, you may need to update the CSS selectors in the script.  
You can change the batch size by editing `BATCH_SIZE` in `scrape_and_analyze.py`.
