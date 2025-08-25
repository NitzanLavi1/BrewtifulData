# 🍺 Beerizer Beer Scraper & LLaVA Label Analysis

This project scrapes beers from [beerizer.com](https://beerizer.com), analyzes each beer label image with LLaVA (via Ollama), and saves results in batches and a master CSV—all outputs go to the `outputs/` folder.

---

## Features

- **Scrapes all beers from Beerizer (1676 pages)**
- **Downloads, analyzes, and deletes each beer image one at a time**
- **Saves every 100 pages to a separate CSV** (`outputs/paginated/beers_1_100.csv`, `outputs/paginated/beers_101_200.csv`, ...)
- **Appends all results to a master CSV** (`outputs/master.csv`)
- **Skips already completed batches for safe resuming**
- **Only includes beers with a valid rating**
- **LLaVA (via Ollama) vision analysis of beer label images**

---

## Requirements

- Python 3.8+
- [Ollama](https://ollama.com/) running locally with a LLaVA model pulled (e.g. `llava:7b`)
- Python packages: `requests`, `beautifulsoup4`, `pandas`

Install dependencies:
```sh
pip install -r requirements.txt
```

---

## Usage

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
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
├── scrape_and_analyze.py      # Scraper and analyzer (functions only)
├── llava_analysis.py          # LLaVA vision analysis integration
├── main.py                    # Official entrypoint
├── config.py                  # All constants and paths
├── runner.py                  # (Optional) Script to run or orchestrate the pipeline
├── outputs/                   # All generated outputs
│   ├── paginated/             # Batch CSVs
│   └── master.csv             # Master CSV
└── ...
```

---

## License

MIT

---

**Tip:**  
If Beerizer changes their HTML, you may need to update the CSS selectors in the script.  
You can change the batch size by editing `BATCH_SIZE` in `config.py`.