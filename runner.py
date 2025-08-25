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

from scrape_and_analyze import run

run()