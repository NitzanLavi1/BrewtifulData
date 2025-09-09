"""
LLaVA Beer Analysis Integration - Direct Image Analysis
------------------------------------------------------
This script analyzes beer labels directly using LLaVA's vision capabilities.
LLaVA can see the actual beer label images and provide detailed analysis.

Requirements:
- Ollama installed and running locally
- LLaVA model pulled (e.g., llava, llava:7b, llava:13b)
- Existing beer metadata from beers.csv
"""

import os
import pandas as pd
import requests
import json
import time
import base64
from typing import Dict, List, Optional
from datetime import datetime
from core.config import BEER_IMAGE_DIR, LLAVA_OUTPUT_CSV, LLAVA_OUTPUT_JSON, LLAVA_BEERS_CSV
import re
import logging

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llava:7b"  # LLaVA model for vision analysis
MAX_RETRIES = 3
RETRY_DELAY = 2
MAX_BEERS = 10  # Limit to 5 beers for testing

def check_ollama_connection():
    """Check if Ollama is running and accessible."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            logger.info(f"Ollama is running. Available models: {[m['name'] for m in models]}")
            return True
        else:
            logger.warning(f"Ollama responded with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Cannot connect to Ollama: {e}")
        logger.error("Make sure Ollama is running: ollama serve")
        return False

def check_llava_model():
    """Check if LLaVA model is available."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            # Check for LLaVA models
            llava_models = [m for m in model_names if 'llava' in m.lower()]
            
            if llava_models:
                logger.info(f"LLaVA models found: {llava_models}")
                return True, llava_models[0]  # Return first available LLaVA model
            else:
                logger.warning("No LLaVA models found")
                logger.info(f"Available models: {model_names}")
                return False, None
        else:
            return False, None
    except Exception as e:
        logger.error(f"Error checking models: {e}")
        return False, None

def encode_image_to_base64(image_path: str) -> str:
    """Encode image to base64 for LLaVA API."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image {image_path}: {e}")
        return ""

def create_llava_prompt(beer_data: Dict) -> str:
    """Create a comprehensive prompt for LLaVA beer label analysis."""
    
    prompt = f"""
Analyze this beer label image for {beer_data['beer_name']} by {beer_data['brewery']} ({beer_data['style']}, {beer_data['abv']}).

Identify the main label color (background color of the label) and the main text color. Respond in this exact JSON format:

{{
    "label_color": "color_name",
    "text_color": "color_name"
}}

Use only basic color names like: black, white, red, blue, green, yellow, orange, purple, brown, gray, gold, silver, pink, etc.
Respond with valid JSON only.
"""
    return prompt

def analyze_beer_with_llava(image_path, beer_data, model_name):
    try:
        image_b64 = encode_image_to_base64(image_path)
        prompt = create_llava_prompt(beer_data)
        payload = {
            "model": model_name,
            "prompt": prompt,
            "images": [image_b64]
        }
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=60
        )

        # Collect all 'response' fragments from the streaming JSON lines
        lines = response.text.strip().splitlines()
        fragments = []
        for line in lines:
            try:
                obj = json.loads(line)
                fragments.append(obj.get("response", ""))
            except Exception:
                pass

        full_response = "".join(fragments)

        # Extract JSON block from the full response
        match = re.search(r'\{[\s\S]*?\}', full_response)
        if match:
            try:
                analysis = json.loads(match.group(0))
                return analysis
            except Exception:
                return create_fallback_analysis(full_response, beer_data)
        else:
            return create_fallback_analysis(full_response, beer_data)
    except Exception as e:
        return {
            "label_color": "N/A",
            "text_color": "N/A",
            "error": str(e)
        }

def create_fallback_analysis(content: str, beer_data: Dict) -> Dict:
    """Create a fallback analysis when JSON parsing fails."""
    logger.info("Creating fallback analysis from text response...")
    
    # Try to extract color information from the text
    content_lower = content.lower()
    
    # Common color names to look for
    colors = ['black', 'white', 'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'brown', 'gray', 'gold', 'silver', 'pink', 'beige', 'cream', 'navy', 'maroon', 'olive', 'teal', 'cyan', 'magenta', 'lime', 'indigo', 'violet', 'tan', 'khaki', 'burgundy', 'crimson', 'emerald', 'turquoise', 'amber', 'copper', 'bronze']
    
    label_color = "unknown"
    text_color = "unknown"
    
    # Look for color mentions in the text
    for color in colors:
        if color in content_lower:
            if label_color == "unknown":
                label_color = color
            elif text_color == "unknown":
                text_color = color
                break
    
    analysis = {
        "label_color": label_color,
        "text_color": text_color,
        "raw_response": content[:500]  # Include first 500 chars of raw response
    }
    
    return analysis

def load_beer_data() -> pd.DataFrame:
    """Load beer metadata from CSV."""
    beers_df = pd.read_csv(LLAVA_BEERS_CSV)
    
    # Clean up URLs in beers_df
    def extract_url(cell):
        if isinstance(cell, str) and cell.startswith('=HYPERLINK('):
            parts = cell.split('"')
            if len(parts) > 1:
                return parts[1]
        return cell
    
    beers_df['URL'] = beers_df['URL'].apply(extract_url)
    
    return beers_df

def save_llava_results(results: List[Dict], output_csv: str = LLAVA_OUTPUT_CSV, output_json: str = LLAVA_OUTPUT_JSON):
    """Save LLaVA analysis results to CSV and JSON files."""
    
    # Save as JSON for detailed analysis
    with open(output_json, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create a flattened CSV for easy viewing
    csv_data = []
    for result in results:
        beer_data = result['beer_data']
        analysis = result['analysis']
        
        analysis_time = result.get('analysis_time', 0)
        
        if 'error' in analysis:
            csv_row = {
                'image_file': beer_data['image_file'],
                'beer_name': beer_data['beer_name'],
                'brewery': beer_data['brewery'],
                'style': beer_data['style'],
                'abv': beer_data['abv'],
                'rating': beer_data.get('rating', 'N/A'),
                'country': beer_data.get('country', 'N/A'),
                'label_color': 'N/A',
                'text_color': 'N/A',
                'analysis_time_seconds': f"{analysis_time:.2f}",
                'error': analysis['error']
            }
        else:
            csv_row = {
                'image_file': beer_data['image_file'],
                'beer_name': beer_data['beer_name'],
                'brewery': beer_data['brewery'],
                'style': beer_data['style'],
                'abv': beer_data['abv'],
                'rating': beer_data.get('rating', 'N/A'),
                'country': beer_data.get('country', 'N/A'),
                'label_color': analysis.get('label_color', 'N/A'),
                'text_color': analysis.get('text_color', 'N/A'),
                'analysis_time_seconds': f"{analysis_time:.2f}",
                'error': 'N/A'
            }
        
        csv_data.append(csv_row)
    
    # Save as CSV
    df = pd.DataFrame(csv_data)
    df.to_csv(output_csv, index=False)
    
    logger.info(f"LLaVA analysis results saved to {output_csv} and {output_json}")