import requests
import json

directories = [
    "https://instances.cobalt.best/api/instances",
    "https://cobalt.directory/api/instances"
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

working_instance = None

print("Fetching instance lists...")
candidate_urls = []

for directory in directories:
    try:
        print(f"Fetching from {directory}...")
        resp = requests.get(directory, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            # Parse list. Structure varies.
            # cobalt.best often returns list of objects with 'protocol', 'url', 'score', etc.
            # cobalt.directory similar.
            
            if isinstance(data, list):
                for item in data:
                    # heuristic to find url
                    u = item.get('url') or item.get('address') or item.get('api')
                    if u:
                        if not u.startswith('http'):
                            u = 'https://' + u
                        candidate_urls.append(u)
            elif isinstance(data, dict):
                 # maybe wrapped
                 print(f"Unknown structure from {directory}")
                 
        else:
            print(f"Failed to fetch {directory}: {resp.status_code}")
    except Exception as e:
        print(f"Error fetching {directory}: {e}")

# Add some hardcoded ones just in case
candidate_urls.extend([
    "https://cobalt.api.redstream.me",
    "https://api.cobalt.tools",
    "https://cobalt.pub",
    "https://cobalt.ops.wtf",
    "https://api.server.cobalt.tools"
])

# Dedup
candidate_urls = list(set(candidate_urls))
print(f"Found {len(candidate_urls)} candidates. Testing...")

for base_url in candidate_urls:
    endpoints = ["/api/json", ""]
    for endpoint in endpoints:
        full_url = base_url.rstrip("/") + endpoint
        try:
            print(f"Testing {full_url}...")
            # Short timeout
            response = requests.post(full_url, json=payload, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "url" in data:
                    print(f"SUCCESS! Found working instance: {base_url}")
                    # Write to file so we can read it
                    with open("working_instance.txt", "w") as f:
                        f.write(base_url)
                    exit(0)
        except:
            pass

print("No working instance found.")
