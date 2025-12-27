"""
Test script for Ollama + Gemini integration
"""
import asyncio
import ollama

async def test_ollama():
    print("Testing Ollama integration...")
    print("\n1. Available models:")
    try:
        models = ollama.list()
        for model in models.get('models', []):
            print(f"   - {model.get('name', 'unknown')}")
    except Exception as e:
        print(f"   Could not list models: {e}")
    
    print("\n2. Testing phi3:mini (fast model):")
    try:
        response = ollama.chat(
            model='phi3:mini',
            messages=[
                {
                    'role': 'user',
                    'content': 'Recommend 3 Indian stocks for a conservative investor. Be brief.'
                }
            ],
            options={
                'temperature': 0.7,
                'num_predict': 256
            }
        )
        print(f"   Response: {response['message']['content'][:200]}...")
        print(f"   ✓ phi3:mini works!")
    except Exception as e:
        print(f"   ✗ phi3:mini failed: {e}")
    
    print("\n3. Testing llama3.1:8b (detailed model):")
    try:
        response = ollama.chat(
            model='llama3.1:8b',
            messages=[
                {
                    'role': 'user',
                    'content': 'Explain the difference between old and new tax regime in India.'
                }
            ],
            options={
                'temperature': 0.7,
                'num_predict': 512
            }
        )
        print(f"   Response: {response['message']['content'][:200]}...")
        print(f"   ✓ llama3.1:8b works!")
    except Exception as e:
        print(f"   ✗ llama3.1:8b failed: {e}")
    
    print("\n✅ Ollama integration test complete!")

if __name__ == "__main__":
    asyncio.run(test_ollama())
