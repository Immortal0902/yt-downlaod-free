import requests
from bs4 import BeautifulSoup
import re

def get_track_info(spotify_url: str):
    """
    Scrapes Spotify URL to get Track Title and Artist.
    Returns dict: {title, artist, search_query, cover_url}
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(spotify_url, headers=headers)
        if response.status_code != 200:
            return {"success": False, "error": f"Failed to fetch Spotify page (Status: {response.status_code})"}

        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to parse title and artist from meta tags (usually reliable)
        title = soup.find("meta", property="og:title")
        description = soup.find("meta", property="og:description")
        image = soup.find("meta", property="og:image")

        if not title:
            # Fallback for newer dynamic pages might need more complex parsing or just return error
            # But usually og:title is present even in SPA
            return {"success": False, "error": "Could not parse track info"}

        track_name = title["content"]
        
        # Description usually "Artist · Song · 2020"
        # We need to extract artist. 
        # For a track, og:title is usually "Song Name - Song by Artist" or just "Song Name"
        # Let's clean it up.
        
        # Simple heuristic:
        # Title: "Song Name"
        # Description: "Listen to Song Name on Spotify. Artist · Song · 2020."
        
        artist_name = "Unknown Artist"
        if description:
            desc_content = description["content"]
            # reliable way is hard without API, but "Artist · Song" pattern is common
            parts = desc_content.split("·")
            if len(parts) >= 2:
                artist_name = parts[0].strip()
        
        # Construct a search query for YouTube
        search_query = f"{track_name} {artist_name} audio"
        
        return {
            "success": True,
            "title": track_name,
            "artist": artist_name,
            "search_query": search_query,
            "cover_url": image["content"] if image else None
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
