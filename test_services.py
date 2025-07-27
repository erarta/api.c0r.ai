#!/usr/bin/env python3
"""
Test script to verify all services can start and communicate
"""
import requests
import json
import time

def test_service_health(service_name, port):
    """Test if a service is responding on given port"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ {service_name} service is healthy on port {port}")
            try:
                data = response.json()
                print(f"   Status: {data.get('status', 'unknown')}")
                print(f"   Service: {data.get('service', 'unknown')}")
            except:
                print(f"   Response: {response.text[:100]}")
            return True
        else:
            print(f"❌ {service_name} service returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {service_name} service not responding: {e}")
        return False

def test_ml_service():
    """Test ML service specific functionality"""
    print("\n🧠 Testing ML Service...")
    
    # Test health endpoint
    if not test_service_health("ML", 8001):
        return False
    
    # Test root endpoint
    try:
        response = requests.get("http://localhost:8001/", timeout=10)
        if response.status_code == 200:
            print("✅ ML service root endpoint working")
            return True
        else:
            print(f"❌ ML service root endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ML service root endpoint error: {e}")
        return False

def test_api_service():
    """Test API service specific functionality"""
    print("\n🤖 Testing API Service...")
    
    # Test health endpoint
    if not test_service_health("API", 8000):
        return False
    
    # Test root endpoint
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            print("✅ API service root endpoint working")
            return True
        else:
            print(f"❌ API service root endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API service root endpoint error: {e}")
        return False

def test_payment_service():
    """Test Payment service if available"""
    print("\n💳 Testing Payment Service...")
    
    # Test if payment service is running
    if test_service_health("Payment", 8002):
        return True
    else:
        print("⚠️  Payment service not running - this is expected if not started yet")
        return False

def main():
    """Main test function"""
    print("🚀 c0r.AI Services Test Suite")
    print("=" * 50)
    
    results = {}
    
    # Test ML Service
    results['ml'] = test_ml_service()
    
    # Test API Service  
    results['api'] = test_api_service()
    
    # Test Payment Service
    results['payment'] = test_payment_service()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    for service, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service.upper()} Service: {'PASS' if status else 'FAIL'}")
    
    working_services = sum(results.values())
    total_services = len(results)
    
    print(f"\n🎯 Overall: {working_services}/{total_services} services working")
    
    if working_services >= 2:  # ML and API are critical
        print("🎉 Core services are operational! Ready for bot testing.")
        return True
    else:
        print("⚠️  Critical services not working. Check logs and configuration.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)