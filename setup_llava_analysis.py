"""
Setup script for LLaVA Beer Analysis
-------------------------------------
This script helps you set up the LLaVA integration for beer analysis.
LLaVA can directly analyze beer label images using vision capabilities.
"""

import os
import sys
import subprocess
import requests

def check_ollama_installation():
    """Check if Ollama is installed."""
    print("🔍 Checking Ollama installation...")
    
    try:
        # Try to run ollama --version
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama is installed but not working properly")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        print("\n📥 To install Ollama:")
        print("1. Visit https://ollama.ai")
        print("2. Download and install for your platform")
        print("3. Or use: curl -fsSL https://ollama.ai/install.sh | sh")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Ollama command timed out")
        return False

def check_ollama_running():
    """Check if Ollama service is running."""
    print("\n🔍 Checking if Ollama service is running...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama is running on http://localhost:11434")
            print(f"📦 Available models: {[m['name'] for m in models]}")
            return True, models
        else:
            print(f"❌ Ollama responded with status code: {response.status_code}")
            return False, []
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("\n🚀 To start Ollama:")
        print("1. Open a terminal")
        print("2. Run: ollama serve")
        print("3. Keep the terminal open")
        return False, []

def suggest_llava_model():
    """Suggest LLaVA models for vision analysis."""
    print("\n🤖 LLaVA Model Selection")
    print("=" * 30)
    
    # List recommended LLaVA models
    recommended_models = [
        "llava:7b",
        "llava:13b", 
        "llava:7b-v1.6",
        "llava:13b-v1.6",
        "llava"
    ]
    
    print("Recommended LLaVA models for beer label analysis:")
    for i, model in enumerate(recommended_models, 1):
        print(f"{i}. {model}")
    
    print("\n💡 Model recommendations:")
    print("- llava:7b: Good balance of speed and accuracy (4GB RAM)")
    print("- llava:13b: Higher accuracy but slower (8GB RAM)")
    print("- llava: Latest version with best performance")
    
    return recommended_models[0]  # Default to llava:7b

def check_llava_models(models):
    """Check if any LLaVA models are available."""
    model_names = [m['name'] for m in models]
    llava_models = [m for m in model_names if 'llava' in m.lower()]
    
    if llava_models:
        print(f"✅ LLaVA models found: {llava_models}")
        return True, llava_models[0]
    else:
        print("❌ No LLaVA models found")
        return False, None

def pull_llava_model(model_name):
    """Pull a LLaVA model from Ollama."""
    print(f"\n📥 Pulling LLaVA model: {model_name}")
    print("This may take 10-30 minutes depending on your internet connection...")
    print("LLaVA models are large (4-8GB) as they include vision capabilities.")
    
    try:
        # Run ollama pull in a subprocess
        process = subprocess.Popen(
            ['ollama', 'pull', model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line.rstrip())
        
        process.wait()
        
        if process.returncode == 0:
            print(f"✅ Successfully pulled {model_name}")
            return True
        else:
            print(f"❌ Failed to pull {model_name}")
            return False
            
    except Exception as e:
        print(f"❌ Error pulling model: {e}")
        return False

def test_llava_analysis():
    """Test the LLaVA analysis with a sample image."""
    print("\n🧪 Testing LLaVA analysis...")
    
    try:
        from llava_analysis import analyze_beer_with_llava
        
        # Check if we have any beer images to test with
        beer_images_dir = "beer_images"
        if not os.path.exists(beer_images_dir):
            print("❌ No beer_images directory found")
            return False
        
        # Find first available image
        image_files = [f for f in os.listdir(beer_images_dir) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if not image_files:
            print("❌ No beer images found in beer_images/ directory")
            return False
        
        test_image = image_files[0]
        print(f"🔍 Testing with image: {test_image}")
        
        # Sample beer data for testing
        sample_beer = {
            'image_file': test_image,
            'beer_name': 'Test Beer',
            'brewery': 'Test Brewery',
            'style': 'Test Style',
            'abv': '5.0%'
        }
        
        print("🔍 Analyzing sample beer label...")
        result = analyze_beer_with_llava(sample_beer)
        
        if 'error' in result:
            print(f"❌ Test failed: {result['error']}")
            return False
        
        print("✅ LLaVA analysis test successful!")
        print("📊 Sample analysis includes:")
        for key in result.keys():
            print(f"   - {key}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'pandas', 'cv2', 'numpy', 'sklearn', 
        'easyocr', 'openpyxl', 'PIL', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'sklearn':
                import sklearn
            elif package == 'PIL':
                import PIL
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_beer_images():
    """Check if beer images are available."""
    print("\n🖼️  Checking beer images...")
    
    beer_images_dir = "beer_images"
    if not os.path.exists(beer_images_dir):
        print("❌ beer_images/ directory not found")
        print("Make sure you have beer label images in the beer_images/ directory")
        return False
    
    image_files = [f for f in os.listdir(beer_images_dir) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not image_files:
        print("❌ No beer images found in beer_images/ directory")
        print("Please add beer label images to analyze")
        return False
    
    print(f"✅ Found {len(image_files)} beer images")
    return True

def main():
    """Main setup function."""
    print("🍺 LLaVA Beer Analysis Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first.")
        return
    
    # Check beer images
    if not check_beer_images():
        print("\n❌ Please ensure beer images are available.")
        return
    
    # Check Ollama installation
    if not check_ollama_installation():
        print("\n❌ Please install Ollama first.")
        return
    
    # Check if Ollama is running
    is_running, models = check_ollama_running()
    if not is_running:
        print("\n❌ Please start Ollama service first.")
        return
    
    # Check for LLaVA models
    has_llava, llava_model = check_llava_models(models)
    
    if not has_llava:
        # Suggest and pull a LLaVA model
        suggested_model = suggest_llava_model()
        
        print(f"\n📥 No LLaVA models found. Pulling {suggested_model}...")
        if not pull_llava_model(suggested_model):
            print(f"\n❌ Failed to pull {suggested_model}")
            print("You can try a different model or check your internet connection.")
            return
    else:
        print(f"✅ LLaVA model {llava_model} is already available")
    
    # Test analysis
    if not test_llava_analysis():
        print("\n❌ Analysis test failed. Please check your setup.")
        return
    
    print("\n🎉 LLaVA setup complete!")
    print("\n📋 Next steps:")
    print("1. Run LLaVA analysis: python3 llava_analysis.py")
    print("2. Check the results in llava_color_analysis.csv and .json files")
    
    print("\n💡 Tips:")
    print("- LLaVA can directly see and analyze beer label images!")
    print("- No need for separate image analysis - LLaVA does it all")
    print("- Each beer analysis uses about 3000 tokens")
    print("- LLaVA models are larger but provide much richer visual analysis")
    print("- You can change the model in llava_analysis.py by modifying DEFAULT_MODEL")

if __name__ == "__main__":
    main()
