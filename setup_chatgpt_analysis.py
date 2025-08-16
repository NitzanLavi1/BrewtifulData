"""
Setup script for ChatGPT Beer Analysis
-------------------------------------
This script helps you set up the ChatGPT integration for beer analysis.
"""

import os
import getpass
import sys

def setup_api_key():
    """Set up the OpenAI API key."""
    print("🔑 Setting up OpenAI API Key for ChatGPT Analysis")
    print("=" * 50)
    
    # Check if API key is already set
    current_key = os.getenv('OPENAI_API_KEY')
    if current_key:
        print(f"✅ OpenAI API key is already set: {current_key[:10]}...")
        response = input("Do you want to update it? (y/n): ").lower()
        if response != 'y':
            return True
    
    print("\n📝 To use ChatGPT analysis, you need an OpenAI API key.")
    print("1. Go to https://platform.openai.com/api-keys")
    print("2. Create a new API key")
    print("3. Copy the key (it starts with 'sk-')")
    print("\n⚠️  Keep your API key secure and never share it!")
    
    # Get API key from user
    api_key = getpass.getpass("Enter your OpenAI API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Setup cancelled.")
        return False
    
    if not api_key.startswith('sk-'):
        print("❌ Invalid API key format. Should start with 'sk-'")
        return False
    
    # Set environment variable
    os.environ['OPENAI_API_KEY'] = api_key
    
    # Test the API key
    print("\n🧪 Testing API key...")
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        
        print("✅ API key is valid!")
        
        # Save to .env file for future use
        with open('.env', 'w') as f:
            f.write(f'OPENAI_API_KEY={api_key}\n')
        print("💾 API key saved to .env file")
        
        return True
        
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'openai', 'pandas', 'cv2', 'numpy', 'sklearn', 
        'easyocr', 'openpyxl', 'PIL'
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

def test_analysis():
    """Test the analysis with a sample beer."""
    print("\n🧪 Testing ChatGPT analysis...")
    
    try:
        from chatgpt_analysis import analyze_beer_with_chatgpt
        
        # Sample beer data for testing
        sample_beer = {
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
        result = analyze_beer_with_chatgpt(sample_beer)
        
        if 'error' in result:
            print(f"❌ Test failed: {result['error']}")
            return False
        
        print("✅ ChatGPT analysis test successful!")
        print("📊 Sample analysis includes:")
        for key in result.keys():
            print(f"   - {key}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🍺 ChatGPT Beer Analysis Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first.")
        return
    
    # Setup API key
    if not setup_api_key():
        print("\n❌ Setup incomplete. Please try again.")
        return
    
    # Test analysis
    if not test_analysis():
        print("\n❌ Analysis test failed. Please check your setup.")
        return
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Run your image analysis: python analyze_images.py")
    print("2. Run ChatGPT analysis: python chatgpt_analysis.py")
    print("3. Check the results in chatgpt_beer_analysis.csv and .json files")
    
    print("\n💡 Tips:")
    print("- The analysis will cost money based on OpenAI's pricing")
    print("- Each beer analysis uses about 2000 tokens")
    print("- You can limit the number of beers analyzed by modifying MAX_IMAGES in analyze_images.py")

if __name__ == "__main__":
    main() 