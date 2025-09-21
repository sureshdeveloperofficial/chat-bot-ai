#!/usr/bin/env python3
"""
Test script to verify all services are working
"""
import requests
import time

def test_service(name, url):
    """Test if a service is responding"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name}: {response.json()}")
            return True
        else:
            print(f"⚠️  {name}: Status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Connection failed (service not running)")
        return False
    except requests.exceptions.Timeout:
        print(f"⏰ {name}: Timeout")
        return False
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False

def test_authentication():
    """Test the authentication flow"""
    print("\n🔐 Testing Authentication...")
    try:
        # Test login
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post("http://localhost:8000/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful")
            return data.get("access_token")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_chat(token):
    """Test the chat functionality"""
    if not token:
        print("❌ No token available for chat test")
        return False
    
    print("\n💬 Testing Chat...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        chat_data = {"message": "Hello, this is a test message"}
        
        response = requests.post("http://localhost:8000/chat", json=chat_data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat successful: {data.get('response', 'No response')[:100]}...")
            return True
        else:
            print(f"❌ Chat failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False

def main():
    print("🧪 Testing Microservice Chatbot")
    print("=" * 40)
    
    # Test all services
    services = [
        ("Auth Service", "http://localhost:8001/health"),
        ("User Service", "http://localhost:8003/health"),
        ("Vector Service", "http://localhost:8004/health"),
        ("Chat Service", "http://localhost:8002/health"),
        ("Gateway", "http://localhost:8000/health"),
    ]
    
    healthy_services = 0
    for name, url in services:
        if test_service(name, url):
            healthy_services += 1
    
    print(f"\n📊 Services Status: {healthy_services}/{len(services)} healthy")
    
    if healthy_services >= 3:  # At least core services running
        # Test authentication and chat
        token = test_authentication()
        test_chat(token)
        
        print(f"\n🎉 Basic functionality test complete!")
        print(f"📱 Access the frontend at: http://localhost:8501")
    else:
        print(f"\n❌ Too few services running. Please check service startup.")
    
    # Test frontend
    print(f"\n🖥️  Testing Frontend...")
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print(f"⚠️  Frontend returned status {response.status_code}")
    except:
        print("❌ Frontend not accessible")

if __name__ == "__main__":
    main()