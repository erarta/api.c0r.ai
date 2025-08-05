#!/usr/bin/env python3
"""
Test script to verify ML service response format
"""

import requests
import json
import base64

def test_ml_service():
    """Test ML service with a simple image"""
    
    # Create a simple test image (1x1 pixel JPEG)
    test_image_data = base64.b64decode(
        "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcU"
        "FhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgo"
        "KCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIA"
        "AhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEB"
        "AQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX"
        "/9k="
    )
    
    # Test the ML service
    url = "http://localhost:8001/api/v1/analyze"
    
    files = {
        'photo': ('test.jpg', test_image_data, 'image/jpeg')
    }
    
    data = {
        'telegram_user_id': '12345',
        'provider': 'openai',
        'user_language': 'en'
    }
    
    try:
        response = requests.post(url, files=files, data=data)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response keys: {list(result.keys())}")
            print(f"Response content: {json.dumps(result, indent=2)}")
            
            # Check if response has the correct format
            if "analysis" in result:
                print("✅ SUCCESS: Response has 'analysis' key")
                return True
            else:
                print("❌ ERROR: Response missing 'analysis' key")
                return False
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Testing ML service response format...")
    success = test_ml_service()
    if success:
        print("\n🎉 Test passed! ML service is returning correct format.")
    else:
        print("\n💥 Test failed! ML service needs fixing.") 