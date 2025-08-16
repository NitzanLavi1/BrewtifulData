"""
Simple Color Extraction from Beer Labels
---------------------------------------
This script extracts only:
- Primary label color
- Secondary label color  
- Primary text color

No ChatGPT analysis, just the raw color data.
"""

import cv2
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import easyocr
import os
from typing import List, Tuple, Dict
import json

def extract_label_colors(image_path: str, k: int = 3) -> List[Tuple[int, int, int]]:
    """
    Extract dominant colors from the entire label image.
    Returns list of RGB tuples, sorted by frequency.
    """
    img = cv2.imread(image_path)
    if img is None:
        return []
    
    # Reshape for clustering
    img_reshaped = img.reshape((-1, 3))
    
    # Use K-means to find dominant colors
    kmeans = KMeans(n_clusters=k, n_init=10)
    kmeans.fit(img_reshaped)
    
    # Get colors and their frequencies
    labels = kmeans.labels_
    colors = kmeans.cluster_centers_.astype(int)
    
    # Count frequency of each color
    color_counts = {}
    for i, label in enumerate(labels):
        color_tuple = tuple(colors[label])
        color_counts[color_tuple] = color_counts.get(color_tuple, 0) + 1
    
    # Sort by frequency (most frequent first)
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [color for color, count in sorted_colors]

def extract_text_regions(image_path: str) -> List[Tuple[int, int, int, int]]:
    """
    Extract regions where text is found using OCR.
    Returns list of (x, y, width, height) bounding boxes.
    """
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(image_path)
    
    text_regions = []
    for detection in result:
        bbox = detection[0]  # Bounding box coordinates
        # Convert to (x, y, width, height) format
        x_coords = [point[0] for point in bbox]
        y_coords = [point[1] for point in bbox]
        
        x = int(min(x_coords))
        y = int(min(y_coords))
        width = int(max(x_coords) - x)
        height = int(max(y_coords) - y)
        
        text_regions.append((x, y, width, height))
    
    return text_regions

def extract_text_colors(image_path: str, k: int = 3) -> List[Tuple[int, int, int]]:
    """
    Extract dominant colors from text regions only.
    Returns list of RGB tuples.
    """
    img = cv2.imread(image_path)
    if img is None:
        return []
    
    # Get text regions
    text_regions = extract_text_regions(image_path)
    
    if not text_regions:
        return []
    
    # Collect all pixels from text regions
    text_pixels = []
    for x, y, width, height in text_regions:
        region = img[y:y+height, x:x+width]
        if region.size > 0:
            text_pixels.extend(region.reshape((-1, 3)))
    
    if not text_pixels:
        return []
    
    text_pixels = np.array(text_pixels)
    
    # Use K-means to find dominant text colors
    kmeans = KMeans(n_clusters=min(k, len(text_pixels)), n_init=10)
    kmeans.fit(text_pixels)
    
    # Get colors and their frequencies
    labels = kmeans.labels_
    colors = kmeans.cluster_centers_.astype(int)
    
    # Count frequency of each color
    color_counts = {}
    for i, label in enumerate(labels):
        color_tuple = tuple(colors[label])
        color_counts[color_tuple] = color_counts.get(color_tuple, 0) + 1
    
    # Sort by frequency (most frequent first)
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [color for color, count in sorted_colors]

def analyze_beer_colors(image_path: str) -> Dict:
    """
    Analyze colors for a single beer image.
    Returns primary/secondary label colors and primary text color.
    """
    try:
        # Extract label colors
        label_colors = extract_label_colors(image_path)
        
        # Extract text colors
        text_colors = extract_text_colors(image_path)
        
        return {
            'primary_label_color': label_colors[0] if label_colors else None,
            'secondary_label_color': label_colors[1] if len(label_colors) > 1 else None,
            'primary_text_color': text_colors[0] if text_colors else None
        }
        
    except Exception as e:
        print(f"Error analyzing colors for {image_path}: {e}")
        return {
            'primary_label_color': None,
            'secondary_label_color': None,
            'primary_text_color': None
        }

def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color string."""
    if rgb is None:
        return None
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

def main():
    """Extract colors from all beer images."""
    print("🎨 Extracting colors from beer labels...")
    
    # Load beer data
    beers_df = pd.read_csv("beers.csv")
    
    # Create mapping from image file to beer data
    beer_data = {}
    for _, row in beers_df.iterrows():
        image_file = row['Image_File']
        beer_data[image_file] = {
            'name': row['Name'],
            'brewery': row['Brewery'],
            'style': row['Style'],
            'abv': row['ABV']
        }
    
    # Process each image
    results = []
    image_dir = "beer_images"
    
    for image_file in os.listdir(image_dir):
        if not image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        
        image_path = os.path.join(image_dir, image_file)
        beer_info = beer_data.get(image_file, {})
        
        print(f"🎨 Processing {image_file}...")
        
        # Extract colors
        colors = analyze_beer_colors(image_path)
        
        # Create result row
        result = {
            'image_file': image_file,
            'beer_name': beer_info.get('name', ''),
            'brewery': beer_info.get('brewery', ''),
            'style': beer_info.get('style', ''),
            'abv': beer_info.get('abv', ''),
            'primary_label_color_rgb': colors['primary_label_color'],
            'secondary_label_color_rgb': colors['secondary_label_color'],
            'primary_text_color_rgb': colors['primary_text_color'],
            'primary_label_color_hex': rgb_to_hex(colors['primary_label_color']),
            'secondary_label_color_hex': rgb_to_hex(colors['secondary_label_color']),
            'primary_text_color_hex': rgb_to_hex(colors['primary_text_color'])
        }
        
        results.append(result)
    
    # Save results
    df = pd.DataFrame(results)
    df.to_csv("beer_colors.csv", index=False)
    
    # Also save as JSON for easy access
    with open("beer_colors.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Extracted colors for {len(results)} beers")
    print("📁 Results saved to beer_colors.csv and beer_colors.json")
    
    # Show sample results
    print("\n📊 Sample results:")
    for result in results[:3]:
        print(f"  {result['beer_name']}:")
        print(f"    Primary label: {result['primary_label_color_hex']} {result['primary_label_color_rgb']}")
        print(f"    Secondary label: {result['secondary_label_color_hex']} {result['secondary_label_color_rgb']}")
        print(f"    Primary text: {result['primary_text_color_hex']} {result['primary_text_color_rgb']}")

if __name__ == "__main__":
    main() 