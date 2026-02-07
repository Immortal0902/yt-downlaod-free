import sys
import os

# Allow running this file directly by adding project root to path
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import yt_dlp
import os
from pathlib import Path
# from app.services.cobalt import get_download_url_with_fallback # Removed

# Make it absolute based on project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

def get_video_info(url: str):
    """
    Get available formats for a YouTube video.
    Returns simplified formats compatible with Cobalt.
    """
    try:
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        formats = []
        seen_res = set()
        
        # We want to find distinct resolutions: 4320p, 2160p, 1440p, 1080p, 720p, 480p, 360p
        # Cobalt supports: max, 2160, 1440, 1080, 720, 480, 360
        supported_res = {2160, 1440, 1080, 720, 480, 360}
        
        for f in info.get('formats', []):
            if f.get('vcodec') != 'none':
                res = f.get('height')
                if res and res in supported_res and res not in seen_res:
                    formats.append({
                        'format_id': str(res), # Use resolution as ID for Cobalt
                        'resolution': f'{res}p',
                        'ext': f['ext'],
                        'filesize': f.get('filesize_approx') or f.get('filesize')
                    })
                    seen_res.add(res)
        
        formats.sort(key=lambda x: int(x['format_id']), reverse=True)
        print(f"DEBUG: Found formats for {url}: {[f['resolution'] for f in formats]}")
        
        return {
            "success": True,
            "title": info.get('title'),
            "thumbnail": info.get('thumbnail'),
            "duration": info.get('duration'),
            "formats": formats,
            "original_url": url
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_youtube(query: str):
    """
    Search YouTube and return the first video URL.
    """
    try:
        ydl_opts = {
            'quiet': True,
            'default_search': 'ytsearch1',
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                first_result = info['entries'][0]
                return {
                    "success": True,
                    "url": first_result['webpage_url'],
                    "title": first_result['title'],
                    "thumbnail": first_result['thumbnail']
                }
            return {"success": False, "error": "No results found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def download_media(url: str, format_id: str = "best"):
    """
    Get direct download URL for the requested format.
    Does NOT download to server.
    """
    try:
        ydl_opts = {
            'quiet': True,
            'format': 'best', # Default fallback
        }
        
        # Audio extraction
        if format_id == 'audio':
            ydl_opts['format'] = 'bestaudio/best'
        # Video resolution
        elif format_id != 'best':
             # Try to get specific height, fallback to best
            ydl_opts['format'] = f'bestvideo[height<={format_id}]+bestaudio/best[height<={format_id}]/best'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 1. Check for 'url' in the main info dict (common for direct video files)
            if 'url' in info:
                return {
                    "success": True,
                    "url": info['url'],
                    "title": info.get('title', 'video'),
                    "is_local": False
                }
            
            # 2. If 'url' not in main dict, it might be in 'formats' or 'requested_downloads'
            # But extract_info(download=False) usually populates 'url' if it's a direct linkable resource.
            # However, for some sites (and complex YouTube streams), 'url' might be a manifest (m3u8).
            # We want the direct media url.
            
            # For YouTube specifically, 'best' format URL is usually available in info['url'] 
            # OR we need to look at info['formats'] for the selected one.
            # But let's trust yt-dlp's format selection from 'ydl_opts' affecting the 'info'.
            # actually extract_info with download=False returns ALL formats. 
            # We need to filter manually if we want a specific one, OR use format_selector.
            
            # Let's refine the strategy:
            # We already passed 'format' to ydl_opts. 
            # Getting the *selected* format url from 'extract_info' without downloading is tricky 
            # because 'extract_info' returns the *video* info which contains *all* formats.
            # We need to pick the best match for our 'format_id'.
            
            # Simple approach: let's iterate formats and pick the best one matching our criteria matching logic used in UI
            
            formats = info.get('formats', [])
            target_url = None
            
            if format_id == 'audio':
                # Find best audio
                best_audio = None
                for f in formats:
                    if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                        if not best_audio or (f.get('filesize') or 0) > (best_audio.get('filesize') or 0):
                            best_audio = f
                if best_audio:
                    target_url = best_audio['url']
            
            else:
                # Video: Find best match for resolution
                # Filter by height if specified
                candidates = []
                for f in formats:
                    if f.get('vcodec') != 'none':
                         # If specific format requested (e.g. 720)
                         h = f.get('height')
                         if format_id != 'best':
                             if h == int(format_id):
                                 candidates.append(f)
                         else:
                             candidates.append(f)
                
                # Sort candidates by bitrate/filesize to get "best" of that resolution
                # Usually the last one in the list is best in yt-dlp sorted list, but let's be safe
                if candidates:
                    target_url = candidates[-1]['url']
            
            # Fallback if manual selection failed but info has url
            if not target_url:
                target_url = info.get('url')
                
            if target_url:
                 return {
                    "success": True,
                    "url": target_url,
                    "title": info.get('title'),
                    "is_local": False
                }
            
            return {"success": False, "error": "Could not extract direct URL"}

    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("This is a support module. To start the app, run 'run_app.py' or 'start_server.bat' in the parent directory.")
    # Optional: Test run if they really want
    # info = get_video_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    # print(info)
