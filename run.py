# run.py
import os
import glob
from typing import Optional

import typer

# Import your modules
import config
from scrape_and_analyze import run_scraping_and_analysis
from llava_analysis import check_llava_model

app = typer.Typer(help="Beer Label Analytics: runner for scraping, analysis, and utilities.")

# ---- Commands ----

@app.command("pipeline")
def pipeline(
    num_pages: Optional[int] = typer.Option(None, help="Override config.NUM_PAGES"),
    batch_size: Optional[int] = typer.Option(None, help="Override config.BATCH_SIZE"),
    output_dir: Optional[str] = typer.Option(None, help="Override config.OUTPUT_DIR"),
):
    """
    Run the full scrape + analysis pipeline.
    """
    if num_pages is not None:
        config.NUM_PAGES = num_pages
    if batch_size is not None:
        config.BATCH_SIZE = batch_size
    if output_dir is not None:
        config.OUTPUT_DIR = output_dir

    typer.echo(f"Starting pipeline with NUM_PAGES={config.NUM_PAGES}, BATCH_SIZE={config.BATCH_SIZE}, OUTPUT_DIR='{config.OUTPUT_DIR}'")
    run_scraping_and_analysis()


@app.command("check")
def check():
    """
    Verify that a LLaVA model is available and print which one.
    Exit code is non-zero if missing (useful for CI).
    """
    has_llava, model = check_llava_model()
    if has_llava:
        typer.echo(f"✅ LLaVA model found: {model}")
        raise typer.Exit(code=0)
    else:
        typer.echo("❌ No LLaVA model found. Please pull/configure a LLaVA model.")
        raise typer.Exit(code=1)


@app.command("clean")
def clean(master: bool = typer.Option(False, "--master", help="Also delete the master CSV.")):
    """
    Delete batch CSVs (and optionally the master CSV).
    """
    deleted = 0
    for path in glob.glob("beers_*.csv"):
        try:
            os.remove(path)
            typer.echo(f"🗑️  deleted {path}")
            deleted += 1
        except Exception as e:
            typer.echo(f"⚠️  failed to delete {path}: {e}")

    if master and os.path.exists(config.MASTER_CSV):
        try:
            os.remove(config.MASTER_CSV)
            typer.echo(f"🗑️  deleted {config.MASTER_CSV}")
        except Exception as e:
            typer.echo(f"⚠️  failed to delete {config.MASTER_CSV}: {e}")

    if deleted == 0 and not master:
        typer.echo("No batch CSVs found.")


@app.command("head")
def head():
    """
    Quick smoke-test run on a very small number of pages.
    """
    original_pages = config.NUM_PAGES
    try:
        config.NUM_PAGES = 1
        typer.echo("Running a quick test on 1 page…")
        run_scraping_and_analysis()
    finally:
        config.NUM_PAGES = original_pages


if __name__ == "__main__":
    app()
