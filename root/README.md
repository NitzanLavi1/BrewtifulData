# 🍺 Beerizer Beer Scraper & LLaVA Label Analysis

This project scrapes beers from [beerizer.com](https://beerizer.com), analyzes each beer label image with LLaVA (via Ollama), and saves results in batches and a master CSV—all outputs go to the `outputs/` folder.

---

## Features

git- **Scrapes all beers from Beerizer**
- **Downloads, analyzes, and deletes each beer image one at a time**
- **Saves every batch of pages to a separate CSV** (`outputs/paginated/beers_1_100.csv`, etc.)
- **Appends all results to a master CSV** (`outputs/master.csv`)
- **Skips already completed batches for safe resuming**
- **Only includes beers with a valid rating**
- **LLaVA (via Ollama) vision analysis of beer label images**
- **Modular code:**  
  - All beer logic in `entities/beer.py`
  - All page scraping logic in `entities/page.py`
  - All CSV logic in `entities/csv_ent.py`
  - Main orchestration in `core/scrape_and_analyze.py` and `root/runner.py`

---

## Requirements

- Python 3.8+
- [Ollama](https://ollama.com/) running locally with a LLaVA model pulled (e.g. `llava:7b`)
- Python packages: `requests`, `beautifulsoup4`, `pandas`

Install dependencies:
```sh
pip install -r root/requirements.txt
```

---

## Usage

1. **Install dependencies:**
   ```sh
   pip install -r root/requirements.txt
   ```

2. **Start Ollama and pull LLaVA:**
   ```sh
   ollama serve
   ollama pull llava:7b
   ```

3. **Run the pipeline:**
   ```sh
   python main.py
   ```

- All batch CSVs will be in `outputs/paginated/`
- The master CSV will be at `outputs/master.csv`

---

## Output

- **Batch CSVs:** `outputs/paginated/beers_1_100.csv`, `outputs/paginated/beers_101_200.csv`, ...  
  Each contains all beers scraped and analyzed in that batch.
- **Master CSV:** `outputs/master.csv`  
  Contains all beers from all batches.
- **Images:** Downloaded and deleted one-by-one during processing.

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
├── core/
│   ├── config.py
│   ├── main.py
│   ├── llava_analysis.py
│   └── scrape_and_analyze.py
├── entities/
│   ├── beer.py
│   ├── csv_ent.py
│   ├── image_manager.py
│   └── page.py
├── outputs/
│   ├── master.csv
│   └── paginated/
├── root/
│   ├── runner.py
│   ├── requirements.txt
│   └── README.md
└── .gitignore
```

---

## License

MIT

---

**Tips:**  
- If Beerizer changes their HTML, you may need to update the CSS selectors in `entities/page.py`.
- You can change the batch size by editing `BATCH_SIZE` in `core/config.py`.