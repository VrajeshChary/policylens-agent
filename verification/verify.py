import requests
import os
import sys

def verify_backend():
    print("Verifying backend...")
    url = "http://localhost:8000/health"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Backend is healthy!")
            return True
        else:
            print(f"Backend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"Failed to connect to backend: {e}")
        return False

if __name__ == "__main__":
    if verify_backend():
        sys.exit(0)
    else:
        sys.exit(1)
