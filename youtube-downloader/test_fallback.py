import sys
import os
from pathlib import Path

# Add current directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.cobalt import get_download_url_with_fallback
from app.services.youtube import download_media

def test_fallback():
    print("Testing Cobalt Fallback Mechanism...")
    
    # Use a short, robust video for testing
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw" # Me at the zoo
    
    print(f"Attempting to download: {test_url}")
    print("This should use yt-dlp locally since Cobalt API is disabled/dead.")
    
    try:
        # Test the direct service call
        result = get_download_url_with_fallback(test_url, video_quality="360")
        
        if result['success']:
            print("SUCCESS: Download successful")
            print(f"URL: {result['url']}")
            print(f"Filename: {result.get('filename')}")
            
            if result['url'].startswith("/files/"):
                print("Pass: URL is serving from local /files/ endpoint")
            else:
                print("Warning: URL is not local (unexpected if Cobalt is down)")
                
            # Check if file exists
            filename = result.get('filename')
            if filename:
                # Based on project root (where this file is)
                scan_dir = Path(__file__).resolve().parent / "downloads"
                local_file = scan_dir / filename
                if local_file.exists():
                     print(f"Pass: File confirmed in {local_file}")
                     # Clean up to save space
                     # os.remove(local_file) 
                     # print("Cleanup: Removed test file")
                else:
                     print(f"Fail: Local file not found at {local_file}")
        else:
            print(f"FAIL: {result.get('error')}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fallback()
