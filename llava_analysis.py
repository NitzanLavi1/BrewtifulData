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

# Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llava:7b"  # LLaVA model for vision analysis
MAX_RETRIES = 3
RETRY_DELAY = 2
MAX_BEERS = 10  # Limit to 5 beers for testing

# File paths
BEERS_CSV = "beers.csv"
OUTPUT_CSV = "llava_colors.csv"
OUTPUT_JSON = "llava_colors.json"

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
                print(f"✅ LLaVA models found: {llava_models}")
                return True, llava_models[0]  # Return first available LLaVA model
            else:
                print("❌ No LLaVA models found")
                print("Available models:", model_names)
                return False, None
        else:
            return False, None
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False, None

def encode_image_to_base64(image_path: str) -> str:
    """Encode image to base64 for LLaVA API."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"❌ Error encoding image {image_path}: {e}")
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

def analyze_beer_with_llava(beer_data: Dict, model: str = DEFAULT_MODEL) -> Dict:
    """Analyze beer label using LLaVA vision model."""
    
    # Get image path
    image_file = beer_data['image_file']
    image_path = os.path.join("beer_images", image_file)
    
    if not os.path.exists(image_path):
        return {"error": f"Image file not found: {image_path}"}
    
    # Encode image to base64
    image_base64 = encode_image_to_base64(image_path)
    if not image_base64:
        return {"error": "Failed to encode image"}
    
    # Create prompt
    prompt = create_llava_prompt(beer_data)
    
    for attempt in range(MAX_RETRIES):
        try:
            # For LLaVA, we need to use the correct API format
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 3000
                }
            }
            
            # Add image data - LLaVA expects images in the payload
            payload["images"] = [image_base64]
            
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=300  # Much longer timeout for vision models (5 minutes)
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
                    
                    # Try to clean up common JSON issues
                    json_str = json_str.replace('\n', ' ').replace('\r', ' ')
                    json_str = ' '.join(json_str.split())  # Remove extra whitespace
                    
                    analysis = json.loads(json_str)
                    return analysis
                    
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error for {beer_data['beer_name']} (attempt {attempt + 1}): {e}")
                    print(f"Raw content preview: {content[:500]}...")
                    
                    # Try to create a fallback analysis from the text
                    try:
                        fallback_analysis = create_fallback_analysis(content, beer_data)
                        return fallback_analysis
                    except:
                        if attempt < MAX_RETRIES - 1:
                            time.sleep(RETRY_DELAY)
                            continue
                        else:
                            return {"error": "Failed to parse LLaVA response", "raw_response": content}
            else:
                print(f"LLaVA API error for {beer_data['beer_name']} (attempt {attempt + 1}): {response.status_code}")
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

def create_fallback_analysis(content: str, beer_data: Dict) -> Dict:
    """Create a fallback analysis when JSON parsing fails."""
    print("🔄 Creating fallback analysis from text response...")
    
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
    beers_df = pd.read_csv(BEERS_CSV)
    
    # Clean up URLs in beers_df
    def extract_url(cell):
        if isinstance(cell, str) and cell.startswith('=HYPERLINK('):
            parts = cell.split('"')
            if len(parts) > 1:
                return parts[1]
        return cell
    
    beers_df['URL'] = beers_df['URL'].apply(extract_url)
    
    return beers_df

def save_llava_results(results: List[Dict], output_csv: str, output_json: str):
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
    
    print(f"✅ LLaVA analysis results saved to {output_csv} and {output_json}")

def main():
    """Main LLaVA analysis pipeline."""
    print("🎨 Starting LLaVA Beer Label Analysis...")
    
    # Check Ollama connection
    if not check_ollama_connection():
        print("❌ Cannot connect to Ollama. Please make sure it's running.")
        return
    
    # Check for LLaVA model
    has_llava, model_name = check_llava_model()
    if not has_llava:
        print("❌ No LLaVA model found. Please pull a LLaVA model first:")
        print("   ollama pull llava")
        print("   or")
        print("   ollama pull llava:7b")
        return
    
    print(f"🤖 Using LLaVA model: {model_name}")
    
    # Load beer data
    print("📊 Loading beer data...")
    beers_df = load_beer_data()
    
    # Filter beers that have images
    beers_with_images = []
    for _, row in beers_df.iterrows():
        image_file = row['Image_File']
        image_path = os.path.join("beer_images", image_file)
        if os.path.exists(image_path):
            beers_with_images.append(row)
    
    print(f"📈 Found {len(beers_with_images)} beers with images to analyze")
    
    if len(beers_with_images) == 0:
        print("❌ No beer images found in beer_images/ directory")
        return
    
    # Analyze each beer (limited to MAX_BEERS)
    results = []
    beers_to_analyze = beers_with_images[:MAX_BEERS]
    
    print(f"📊 Analyzing {len(beers_to_analyze)} beers (limited to {MAX_BEERS})...")
    
    for idx, row in enumerate(beers_to_analyze):
        beer_data = {
            'image_file': row['Image_File'],
            'beer_name': row['Name'],
            'brewery': row['Brewery'],
            'style': row['Style'],
            'abv': row['ABV'],
            'price': row['Price'],
            'rating': row['Rating'],
            'country': row.get('Country', 'Unknown')
        }
        
        beer_name = beer_data['beer_name'] or beer_data['image_file']
        print(f"🎨 Analyzing {beer_name} ({idx + 1}/{len(beers_to_analyze)})...")
        
        # Start timing
        start_time = time.time()
        
        analysis = analyze_beer_with_llava(beer_data, model_name)
        
        # End timing
        end_time = time.time()
        analysis_time = end_time - start_time
        
        print(f"⏱️  Analysis completed in {analysis_time:.2f} seconds")
        
        results.append({
            'beer_data': beer_data,
            'analysis': analysis,
            'analysis_time': analysis_time
        })
        
        # Rate limiting - wait between requests
        # time.sleep(2)  # <-- Comment out or reduce this delay
    
    # Save results
    print("💾 Saving LLaVA analysis results...")
    save_llava_results(results, OUTPUT_CSV, OUTPUT_JSON)
    
    # Calculate timing summary
    total_time = sum(result.get('analysis_time', 0) for result in results)
    avg_time = total_time / len(results) if results else 0
    
    print("🎉 LLaVA analysis complete!")
    print(f"📊 Timing Summary:")
    print(f"   Total analysis time: {total_time:.2f} seconds")
    print(f"   Average time per beer: {avg_time:.2f} seconds")
    print(f"   Beers analyzed: {len(results)}")
    print(f"📁 Check {OUTPUT_CSV} for summary results")
    print(f"📁 Check {OUTPUT_JSON} for detailed visual analysis")

if __name__ == "__main__":
    main()
