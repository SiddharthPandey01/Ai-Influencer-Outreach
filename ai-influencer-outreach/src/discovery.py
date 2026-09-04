import os
import sys
import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def discover_influencers(api_key=None, max_results=100):
    """
    Discover YouTube influencers in the AI/tech niche.
    If api_key is provided, uses YouTube Data API v3.
    If not, falls back to sample data.
    """
    if api_key:
        print("Using YouTube API for discovery...")
        try:
            return _search_youtube(api_key, max_per_term=max_results)
        except Exception as e:
            print(f"YouTube API failed: {e}. Falling back to sample data.")
            return _use_sample_data()
    else:
        print("No API key provided, using sample data...")
        return _use_sample_data()

def _search_youtube(api_key, search_terms=None, max_per_term=15):
    """Use YouTube Data API v3 to search for channels."""
    try:
        from googleapiclient.discovery import build
    except ImportError:
        raise ImportError("google-api-python-client is not installed.")
        
    if not search_terms:
        search_terms = ['AI tools', 'Generative AI', 'Machine Learning', 'Python tutorial', 'LLM tutorial', 'RAG tutorial', 'LangChain', 'deep learning', 'artificial intelligence', 'data science Python']
        
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    influencers = []
    seen_ids = set()
    
    for term in search_terms:
        try:
            search_response = youtube.search().list(
                q=term,
                type='channel',
                part='id',
                maxResults=max_per_term
            ).execute()
            
            channel_ids = [item['id']['channelId'] for item in search_response.get('items', [])]
            
            if not channel_ids:
                continue
                
            channels_response = youtube.channels().list(
                id=','.join(channel_ids),
                part='snippet,statistics'
            ).execute()
            
            for channel in channels_response.get('items', []):
                cid = channel['id']
                if cid in seen_ids:
                    continue
                seen_ids.add(cid)
                
                snippet = channel.get('snippet', {})
                stats = channel.get('statistics', {})
                
                influencers.append({
                    'name': snippet.get('title', ''),
                    'platform': 'YouTube',
                    'profile_url': f"https://youtube.com/channel/{cid}",
                    'channel_id': cid,
                    'followers': int(stats.get('subscriberCount', 0)),
                    'description': snippet.get('description', ''),
                    'video_count': int(stats.get('videoCount', 0)),
                    'view_count': int(stats.get('viewCount', 0))
                })
        except Exception as e:
            print(f"Error searching term '{term}': {e}")
            
    return pd.DataFrame(influencers)

def _use_sample_data():
    """Fall back to sample data when no API key is available."""
    from src.sample_data import get_sample_influencers
    return pd.DataFrame(get_sample_influencers())

def save_raw_data(df, path=None):
    """Save DataFrame to data/raw_influencers.csv"""
    if path is None:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw_influencers.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Raw data saved to {path}")
    return path
