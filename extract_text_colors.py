"""
Text Color Extraction from Beer Labels
-------------------------------------
This script extracts actual text colors from beer label images by analyzing
the regions where OCR text was detected.
"""

import cv2
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import easyocr
import os
from typing import List, Tuple, Dict

def extract_text_regions(image_path: str) -> List[Tuple[int, int, int, int]]:
    """
    Extract regions where text is likely to be found using OCR.
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

def extract_colors_from_regions(image_path: str, regions: List[Tuple[int, int, int, int]], k: int = 3) -> List[List[Tuple[int, int, int]]]:
    """
    Extract dominant colors from specific regions in the image.
    Returns list of color lists for each region.
    """
    img = cv2.imread(image_path)
    if img is None:
        return []
    
    region_colors = []
    
    for x, y, width, height in regions:
        # Extract the region
        region = img[y:y+height, x:x+width]
        
        if region.size == 0:
            continue
        
        # Reshape for clustering
        region_reshaped = region.reshape((-1, 3))
        
        # Use K-means to find dominant colors
        kmeans = KMeans(n_clusters=min(k, len(region_reshaped)), n_init=10)
        kmeans.fit(region_reshaped)
        
        # Get the dominant colors
        colors = kmeans.cluster_centers_.astype(int)
        region_colors.append([tuple(color) for color in colors])
    
    return region_colors

def analyze_text_colors(image_path: str) -> Dict:
    """
    Analyze text colors in a beer label image.
    Returns dictionary with text regions and their colors.
    """
    try:
        # Extract text regions
        text_regions = extract_text_regions(image_path)
        
        if not text_regions:
            return {
                'text_regions': [],
                'text_colors': [],
                'primary_text_color': None,
                'text_color_variety': 0
            }
        
        # Extract colors from text regions
        region_colors = extract_colors_from_regions(image_path, text_regions)
        
        # Flatten all text colors
        all_text_colors = []
        for colors in region_colors:
            all_text_colors.extend(colors)
        
        # Find the most common text color (primary text color)
        if all_text_colors:
            # Simple approach: take the first color as primary
            primary_color = all_text_colors[0]
        else:
            primary_color = None
        
        return {
            'text_regions': text_regions,
            'text_colors': region_colors,
            'primary_text_color': primary_color,
            'text_color_variety': len(set(all_text_colors))
        }
        
    except Exception as e:
        print(f"Error analyzing text colors for {image_path}: {e}")
        return {
            'text_regions': [],
            'text_colors': [],
            'primary_text_color': None,
            'text_color_variety': 0
        }

def main():
    """Test the text color extraction on a few sample images."""
    image_dir = "beer_images"
    
    # Test on first few images
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))][:3]
    
    for image_file in image_files:
        image_path = os.path.join(image_dir, image_file)
        print(f"\n🎨 Analyzing text colors in {image_file}...")
        
        result = analyze_text_colors(image_path)
        
        print(f"   Text regions found: {len(result['text_regions'])}")
        print(f"   Primary text color: {result['primary_text_color']}")
        print(f"   Color variety: {result['text_color_variety']} different colors")
        
        if result['text_colors']:
            print("   Text colors by region:")
            for i, colors in enumerate(result['text_colors']):
                print(f"     Region {i+1}: {colors}")

if __name__ == "__main__":
    main() 