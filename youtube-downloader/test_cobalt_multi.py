import requests
import json

urls_to_test = [
    "https://api.cobalt.tools", # Try root endpoint
    "https://cobalt.api.redstream.me",
    "https://co.wuk.sh/api/json", # Older style?
    "https://api.server.cobalt.tools", # Sometimes used
]

test_video = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

payload = {
    "url": test_video,
    "vQuality": "360"
}

for base_url in urls_to_test:
    # Try /api/json first (v7 style)
    endpoints = ["/api/json", ""]
    
    for endpoint in endpoints:
        full_url = base_url.rstrip("/") + endpoint
        try:
            print(f"Testing {full_url}...")
            response = requests.post(full_url, json=payload, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "url" in data:
                    print(f"SUCCESS with {full_url}")
                    print(json.dumps(data, indent=2))
                    exit(0)
                else:
                    print(f"Failed logic with {full_url}: {data}")
            else:
                 print(f"HTTP {response.status_code} from {full_url}: {response.text[:200]}")
        except Exception as e:
            print(f"Error connecting to {full_url}: {e}")

print("All tests failed.")
