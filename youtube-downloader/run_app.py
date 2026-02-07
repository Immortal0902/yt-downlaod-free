import uvicorn
import os
import sys

# Ensure the current directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Run the FastAPI app using Uvicorn
    # reload=True allows auto-restart on code changes (great for dev)
    print("Starting YouTube & Spotify Downloader...")
    print("Open http://localhost:8000 in your browser.")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
