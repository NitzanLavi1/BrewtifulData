"""
Setup script for Ollama Beer Analysis
-------------------------------------
This script helps you set up the Ollama integration for beer analysis.
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

def suggest_model():
    """Suggest a model to use for analysis."""
    print("\n🤖 Model Selection")
    print("=" * 30)
    
    # List recommended models
    recommended_models = [
        "llama3.2",
        "llama3.2:3b", 
        "mistral",
        "codellama",
        "llama3.1:8b"
    ]
    
    print("Recommended models for beer analysis:")
    for i, model in enumerate(recommended_models, 1):
        print(f"{i}. {model}")
    
    print("\n💡 For best results, use llama3.2 or mistral")
    print("💡 For faster processing, use llama3.2:3b")
    
    return recommended_models[0]  # Default to llama3.2

def pull_model(model_name):
    """Pull a model from Ollama."""
    print(f"\n📥 Pulling model: {model_name}")
    print("This may take several minutes depending on your internet connection...")
    
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

def test_ollama_analysis():
    """Test the Ollama analysis with a sample beer."""
    print("\n🧪 Testing Ollama analysis...")
    
    try:
        from ollama_analysis import analyze_colors_with_ollama
        
        # Sample beer data for testing
        sample_beer = {
            'image_file': 'test.jpg',
            'beer_name': 'Test IPA',
            'brewery': 'Test Brewery',
            'style': 'IPA - American',
            'abv': '6.5%',
            'price': '8.99',
            'rating': '4.2',
            'ocr_text': 'IPA Test Brewery',
            'label_colors': '[(255, 0, 0), (255, 255, 0), (0, 0, 255)]',
            'bottle_colors': '[(255, 255, 255), (200, 200, 200), (100, 100, 100)]',
            'beer_url': 'https://example.com'
        }
        
        print("🔍 Analyzing sample beer...")
        result = analyze_colors_with_ollama(sample_beer)
        
        if 'error' in result:
            print(f"❌ Test failed: {result['error']}")
            return False
        
        print("✅ Ollama analysis test successful!")
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

def main():
    """Main setup function."""
    print("🍺 Ollama Beer Analysis Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first.")
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
    
    # Suggest and pull a model if needed
    suggested_model = suggest_model()
    
    # Check if the suggested model is available
    available_models = [m['name'] for m in models]
    if suggested_model not in available_models:
        print(f"\n📥 Model {suggested_model} not found. Pulling...")
        if not pull_model(suggested_model):
            print(f"\n❌ Failed to pull {suggested_model}")
            print("You can try a different model or check your internet connection.")
            return
    else:
        print(f"✅ Model {suggested_model} is already available")
    
    # Test analysis
    if not test_ollama_analysis():
        print("\n❌ Analysis test failed. Please check your setup.")
        return
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Run your image analysis: python analyze_images.py")
    print("2. Run Ollama analysis: python ollama_analysis.py")
    print("3. Check the results in ollama_color_analysis.csv and .json files")
    
    print("\n💡 Tips:")
    print("- Ollama runs locally, so no API costs!")
    print("- Each beer analysis uses about 2000 tokens")
    print("- You can limit the number of beers analyzed by modifying MAX_IMAGES in analyze_images.py")
    print("- You can change the model in ollama_analysis.py by modifying DEFAULT_MODEL")

if __name__ == "__main__":
    main()
