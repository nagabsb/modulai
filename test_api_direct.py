import requests

# Test Gemini API directly
api_key = "AIzaSyBfgyrOY1xEtTErFLPjh8kqFC4fRwjfLO0"

# List available models
print("Testing Gemini API key and listing available models...")

try:
    response = requests.get(
        f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        models = response.json()
        print(f"✅ API key is valid. Found {len(models.get('models', []))} models:")
        
        for model in models.get('models', []):
            name = model.get('name', '')
            display_name = model.get('displayName', '')
            supported_methods = model.get('supportedGenerationMethods', [])
            
            print(f"- {name} ({display_name}) - Methods: {supported_methods}")
    else:
        print(f"❌ API call failed: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test a simple generation with gemini-1.5-flash
print("\nTesting document generation with gemini-1.5-flash...")

test_prompt = "Buatkan 1 soal pilihan ganda tentang rangkaian listrik untuk kelas 10 SMA"

payload = {
    "contents": [{
        "parts": [{
            "text": test_prompt
        }]
    }],
    "generationConfig": {
        "temperature": 0.7,
        "topK": 40,
        "topP": 0.95,
        "maxOutputTokens": 1024,
    }
}

try:
    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
        json=payload,
        timeout=30
    )
    
    print(f"Generation Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        print(f"✅ Generation successful! Content preview: {content[:200]}...")
    else:
        print(f"❌ Generation failed: {response.text}")
        
except Exception as e:
    print(f"❌ Generation error: {e}")