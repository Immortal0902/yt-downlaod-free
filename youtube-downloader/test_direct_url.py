
import sys
import os
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from app.services.youtube import download_media

def test_direct_url():
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Rick Roll - usually available
    print(f"Testing direct URL extraction for: {test_url}")
    
    result = download_media(test_url, format_id="best")
    
    if result.get("success"):
        print("SUCCESS: Got direct URL")
        print(f"URL: {result['url'][:50]}...") # Print first 50 chars
        if not result['url'].startswith("http"):
             print("FAILURE: URL does not start with http")
        else:
             print("VERIFIED: URL is valid")
    else:
        print(f"FAILURE: {result.get('error')}")

if __name__ == "__main__":
    test_direct_url()
