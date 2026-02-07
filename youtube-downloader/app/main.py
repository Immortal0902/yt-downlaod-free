import sys
import os

# Allow running this file directly by adding project root to path
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path

from app.services.youtube import get_video_info, search_youtube, download_media
from app.services.spotify import get_track_info
# from app.utils.keep_alive import start_keep_alive # Removed

app = FastAPI(title="YT & Spotify Downloader")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Mount Static Files
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")

# Expose Downloads - REMOVED for Serverless
# We no longer save files locally.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Keep-Alive task removed for serverless compatibility
    pass

@app.get("/")
async def root():
    return FileResponse(BASE_DIR / 'app/static/index.html')

@app.get("/api/info")
async def get_info(url: str):
    """
    Smart Info Fetcher.
    Detects if Spotify or YouTube URL.
    """
    if "spotify.com" in url:
        # 1. Scrap Spotify Info
        sp_data = get_track_info(url)
        if not sp_data['success']:
            raise HTTPException(status_code=400, detail=sp_data['error'])
        
        # 2. Search on YouTube
        yt_search = search_youtube(sp_data['search_query'])
        if not yt_search['success']:
             raise HTTPException(status_code=404, detail="Could not find match on YouTube")
        
        # 3. Get Formats for the YouTube Video
        yt_info = get_video_info(yt_search['url'])
        
        # Merge Data to show user what we found
        return {
            "type": "spotify",
            "spotify_meta": sp_data,
            "youtube_match": yt_info
        }
        
    elif "youtube.com" in url or "youtu.be" in url:
        # Direct YouTube
        yt_info = get_video_info(url)
        if not yt_info['success']:
            raise HTTPException(status_code=400, detail=yt_info['error'])
        
        return {
            "type": "youtube",
            "youtube_match": yt_info
        }
        
    else:
        raise HTTPException(status_code=400, detail="Unsupported URL. Use YouTube or Spotify links.")

@app.get("/api/download")
def download(url: str, format_id: str = "best"):
    """
    Download endpoint.
    """
    result = download_media(url, format_id)
    if not result['success']:
        raise HTTPException(status_code=500, detail=result['error'])
    
    return result

@app.get("/health")
def health():
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    print("Starting app directly...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
