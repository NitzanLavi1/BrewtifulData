"""
Ollama Beer Analysis Integration - Label & Text Colors Only
-----------------------------------------------------------
This script analyzes beer labels focusing only on:
- Label background colors
- Text colors on the label

Requirements:
- Ollama installed and running locally
- A model pulled (e.g., llama3.2, mistral, codellama)
- Existing beer analysis data from analyze_images.py
"""

import os
import pandas as pd
import requests
import json
import time
from typing import Dict, List, Optional
from datetime import datetime

# Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"  # Change this to your preferred model
MAX_RETRIES = 3
RETRY_DELAY = 2

# File paths
ANALYSIS_CSV = "beer_label_analysis.csv"
BEERS_CSV = "beers.csv"
OUTPUT_CSV = "ollama_color_analysis.csv"
OUTPUT_JSON = "ollama_color_analysis.json"

def check_ollama_connection():
    """Check if Ollama is running and accessible."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama is running. Available models: {[m['name'] for m in models]}")
            return True
        else:
            print(f"❌ Ollama responded with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("Make sure Ollama is running: ollama serve")
        return False

def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the analysis data and beer metadata."""
    analysis_df = pd.read_csv(ANALYSIS_CSV)
    beers_df = pd.read_csv(BEERS_CSV)
    
    # Clean up URLs in beers_df
    def extract_url(cell):
        if isinstance(cell, str) and cell.startswith('=HYPERLINK('):
            parts = cell.split('"')
            if len(parts) > 1:
                return parts[1]
        return cell
    
    beers_df['URL'] = beers_df['URL'].apply(extract_url)
    
    return analysis_df, beers_df

def merge_data(analysis_df: pd.DataFrame, beers_df: pd.DataFrame) -> pd.DataFrame:
    """Merge analysis data with beer metadata."""
    # Create a mapping from image file to beer data
    beer_data = {}
    for _, row in beers_df.iterrows():
        image_file = row['Image_File']
        beer_data[image_file] = {
            'name': row['Name'],
            'brewery': row['Brewery'],
            'price': row['Price'],
            'rating': row['Rating'],
            'abv': row['ABV'],
            'style': row['Style']
        }
    
    # Add beer metadata to analysis data
    merged_data = []
    for _, row in analysis_df.iterrows():
        image_file = row['Image_File']
        beer_info = beer_data.get(image_file, {})
        
        merged_row = {
            'image_file': image_file,
            'ocr_text': row['OCR_Text'],
            'label_colors': row['Label_Colors'],
            'bottle_colors': row['Bottle_Colors'],
            'beer_url': row['Beer_URL'],
            'beer_name': beer_info.get('name', ''),
            'brewery': beer_info.get('brewery', ''),
            'price': beer_info.get('price', ''),
            'rating': beer_info.get('rating', ''),
            'abv': beer_info.get('abv', ''),
            'style': beer_info.get('style', '')
        }
        merged_data.append(merged_row)
    
    return pd.DataFrame(merged_data)

def extract_text_colors_from_image(image_file: str) -> List:
    """
    Extract actual text colors from the beer label image.
    """
    try:
        from extract_text_colors import analyze_text_colors
        
        image_path = os.path.join("beer_images", image_file)
        if not os.path.exists(image_path):
            return []
        
        result = analyze_text_colors(image_path)
        
        # Extract all text colors
        all_text_colors = []
        for colors in result.get('text_colors', []):
            all_text_colors.extend(colors)
        
        return all_text_colors
        
    except Exception as e:
        print(f"Error extracting text colors from {image_file}: {e}")
        return []

def create_color_analysis_prompt(beer_data: Dict) -> str:
    """Create a focused prompt for label and text color analysis."""
    
    # Parse colors from string representation
    def parse_colors(color_str):
        try:
            if isinstance(color_str, str):
                return eval(color_str)
            return color_str
        except:
            return []
    
    label_colors = parse_colors(beer_data['label_colors'])
    bottle_colors = parse_colors(beer_data['bottle_colors'])
    
    # Extract actual text colors from the image
    text_colors = extract_text_colors_from_image(beer_data['image_file'])
    
    prompt = f"""
You are a beer label design expert. Analyze this beer's label focusing ONLY on colors:

BEER INFORMATION:
- Name: {beer_data['beer_name']}
- Brewery: {beer_data['brewery']}
- Style: {beer_data['style']}
- ABV: {beer_data['abv']}

COLOR ANALYSIS:
- Label Background Colors (RGB): {label_colors}
- Text Colors (RGB): {text_colors}
- OCR Text Found: "{beer_data['ocr_text']}"

Please provide analysis in JSON format with this structure:

{{
    "label_colors": {{
        "primary_color": "Main background color description",
        "secondary_colors": ["Other background colors"],
        "color_scheme": "Overall color scheme (e.g., warm, cool, neutral, bold, subtle)",
        "color_psychology": "What these colors suggest about the beer"
    }},
    "text_colors": {{
        "primary_text_color": "Main text color description",
        "contrast_analysis": "How well text colors contrast with background",
        "readability": "Text readability assessment (good/fair/poor)",
        "text_color_psychology": "What the text colors suggest"
    }},
    "color_effectiveness": {{
        "style_match": "How well colors match the beer style",
        "brand_identity": "How colors contribute to brand identity",
        "shelf_appeal": "How colors affect shelf appeal (1-10 score)",
        "overall_assessment": "Brief overall color assessment"
    }}
}}

Focus ONLY on color analysis. Be specific about what the colors suggest about the beer's character, style, and target audience. Respond with valid JSON only.
"""
    return prompt

def analyze_colors_with_ollama(beer_data: Dict, model: str = DEFAULT_MODEL) -> Dict:
    """Analyze label and text colors using Ollama."""
    
    prompt = create_color_analysis_prompt(beer_data)
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 2000
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                content = response.json().get('response', '')
                
                # Try to extract JSON from the response
                try:
                    # Look for JSON in the response
                    if '```json' in content:
                        json_start = content.find('```json') + 7
                        json_end = content.find('```', json_start)
                        json_str = content[json_start:json_end].strip()
                    elif '{' in content and '}' in content:
                        json_start = content.find('{')
                        json_end = content.rfind('}') + 1
                        json_str = content[json_start:json_end]
                    else:
                        json_str = content
                    
                    analysis = json.loads(json_str)
                    return analysis
                    
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error for {beer_data['beer_name']} (attempt {attempt + 1}): {e}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                        continue
                    else:
                        return {"error": "Failed to parse Ollama response"}
            else:
                print(f"Ollama API error for {beer_data['beer_name']} (attempt {attempt + 1}): {response.status_code}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    return {"error": f"API error: {response.status_code}"}
                    
        except requests.exceptions.RequestException as e:
            print(f"Request error for {beer_data['beer_name']} (attempt {attempt + 1}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            else:
                return {"error": f"Request error: {str(e)}"}
    
    return {"error": "Max retries exceeded"}

def save_color_results(results: List[Dict], output_csv: str, output_json: str):
    """Save color analysis results to CSV and JSON files."""
    
    # Save as JSON for detailed analysis
    with open(output_json, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create a flattened CSV for easy viewing
    csv_data = []
    for result in results:
        beer_data = result['beer_data']
        analysis = result['analysis']
        
        if 'error' in analysis:
            csv_row = {
                'image_file': beer_data['image_file'],
                'beer_name': beer_data['beer_name'],
                'brewery': beer_data['brewery'],
                'style': beer_data['style'],
                'abv': beer_data['abv'],
                'label_colors': beer_data['label_colors'],
                'text_colors': 'N/A',
                'color_scheme': 'N/A',
                'contrast_analysis': 'N/A',
                'readability': 'N/A',
                'shelf_appeal': 'N/A',
                'overall_assessment': f"Error: {analysis['error']}"
            }
        else:
            csv_row = {
                'image_file': beer_data['image_file'],
                'beer_name': beer_data['beer_name'],
                'brewery': beer_data['brewery'],
                'style': beer_data['style'],
                'abv': beer_data['abv'],
                'label_colors': beer_data['label_colors'],
                'text_colors': analysis.get('text_colors', {}).get('primary_text_color', 'N/A'),
                'color_scheme': analysis.get('label_colors', {}).get('color_scheme', 'N/A'),
                'contrast_analysis': analysis.get('text_colors', {}).get('contrast_analysis', 'N/A'),
                'readability': analysis.get('text_colors', {}).get('readability', 'N/A'),
                'shelf_appeal': analysis.get('color_effectiveness', {}).get('shelf_appeal', 'N/A'),
                'overall_assessment': analysis.get('color_effectiveness', {}).get('overall_assessment', 'N/A')
            }
        
        csv_data.append(csv_row)
    
    # Save as CSV
    df = pd.DataFrame(csv_data)
    df.to_csv(output_csv, index=False)
    
    print(f"✅ Color analysis results saved to {output_csv} and {output_json}")

def main():
    """Main color analysis pipeline."""
    print("🎨 Starting Ollama Color Analysis...")
    
    # Check Ollama connection
    if not check_ollama_connection():
        print("❌ Cannot connect to Ollama. Please make sure it's running.")
        return
    
    # Load and merge data
    print("📊 Loading data...")
    analysis_df, beers_df = load_data()
    merged_df = merge_data(analysis_df, beers_df)
    
    print(f"📈 Found {len(merged_df)} beers to analyze for colors")
    
    # Analyze each beer's colors
    results = []
    for idx, row in merged_df.iterrows():
        beer_data = row.to_dict()
        beer_name = beer_data['beer_name'] or beer_data['image_file']
        
        print(f"🎨 Analyzing colors for {beer_name} ({idx + 1}/{len(merged_df)})...")
        
        analysis = analyze_colors_with_ollama(beer_data)
        
        results.append({
            'beer_data': beer_data,
            'analysis': analysis
        })
        
        # Rate limiting - wait between requests
        time.sleep(1)
    
    # Save results
    print("💾 Saving color analysis results...")
    save_color_results(results, OUTPUT_CSV, OUTPUT_JSON)
    
    print("🎉 Color analysis complete!")
    print(f"📁 Check {OUTPUT_CSV} for summary results")
    print(f"📁 Check {OUTPUT_JSON} for detailed color analysis")

if __name__ == "__main__":
    main()
