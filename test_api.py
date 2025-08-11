import requests
import json
import time

def test_store_creation():
    base_url = "http://127.0.0.1:5000"
    
    print("Testing Flask API...")
    
    # Test 1: Check if server is responding
    try:
        response = requests.get(f"{base_url}/api/config", timeout=5)
        print(f"✅ Config endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Config endpoint failed: {e}")
        return
    
    # Test 2: Create a store
    print("\nTesting store creation...")
    payload = {
        "prompt": "add some workout clothes for men and women to the store"
    }
    
    try:
        response = requests.post(f"{base_url}/api/create-store", json=payload, timeout=10)
        print(f"✅ Store creation request: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get('job_id')
            print(f"   Job ID: {job_id}")
            
            # Poll for completion
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                status_response = requests.get(f"{base_url}/api/job-status/{job_id}", timeout=5)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    progress = status_data.get('progress', 0)
                    print(f"   Status: {status} ({progress}%)")
                    
                    if status in ['completed', 'failed']:
                        print(f"   Final result: {json.dumps(status_data, indent=2)}")
                        break
                else:
                    print(f"   Status check failed: {status_response.status_code}")
                    break
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Store creation failed: {e}")

if __name__ == "__main__":
    test_store_creation()
