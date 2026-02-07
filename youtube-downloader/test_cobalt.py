from app.services.cobalt import get_cobalt_url
import json

# Test with a known safe video (compilation or creative commons)
# Rick Roll is a standard test case: https://www.youtube.com/watch?v=dQw4w9WgXcQ
test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

print(f"Testing Cobalt API with URL: {test_url}")
result = get_cobalt_url(test_url, video_quality="720")
print(json.dumps(result, indent=2))

if result.get("success") and result.get("url"):
    print("SUCCESS: Got download URL")
else:
    print("FAILURE: Did not get download URL")
