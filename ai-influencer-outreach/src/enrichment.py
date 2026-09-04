import os
import sys
import pandas as pd
import re
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def extract_email(text):
    """Extract email from text using regex."""
    if not isinstance(text, str):
        return 'Not Found'
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, text)
    for m in matches:
        if m.lower() != 'example@example.com':
            return m
    return 'Not Found'

def calculate_engagement_rate(view_count, followers, video_count):
    """
    YouTube-specific engagement rate.
    Formula: (Average Views per Video / Subscribers) * 100
    """
    try:
        vc = float(view_count)
        f = float(followers)
        vidc = float(video_count)
        
        avg_views = vc / vidc if vidc > 0 else 0
        rate = (avg_views / f) * 100 if f > 0 else 0
        return round(rate, 2)
    except:
        return 0.0

def _determine_niche(description):
    """Determine specific niche from description keywords."""
    desc = str(description).lower()
    if 'generative ai' in desc or 'gen ai' in desc:
        return 'Generative AI'
    elif 'machine learning' in desc or 'ml' in desc:
        return 'Machine Learning'
    elif 'data science' in desc:
        return 'Data Science'
    elif 'ai/ml' in desc or 'ai' in desc:
        return 'AI/ML'
    elif 'python' in desc:
        return 'Python Development'
    else:
        return 'Technology'

def _extract_content_themes(description):
    """Extract content themes from description."""
    desc = str(description).lower()
    themes = []
    
    if 'llm' in desc or 'gpt' in desc:
        themes.append('Large Language Models')
    if 'rag' in desc:
        themes.append('RAG Systems')
    if 'langchain' in desc:
        themes.append('LangChain')
    if 'computer vision' in desc:
        themes.append('Computer Vision')
    if 'nlp' in desc:
        themes.append('NLP')
    if 'tutorial' in desc or 'course' in desc:
        themes.append('Tutorials')
        
    return ','.join(themes[:5]) if themes else 'General Tech'

def enrich_profile(row):
    """Enrich a single influencer profile."""
    desc = str(row.get('description', ''))
    
    email = extract_email(desc)
    
    # website extraction
    website_match = re.search(r'(https?://[^\s]+)', desc)
    website = website_match.group(1) if website_match else 'Not Found'
    
    engagement_rate = calculate_engagement_rate(
        row.get('view_count', 0),
        row.get('followers', 0),
        row.get('video_count', 0)
    )
    
    niche = _determine_niche(desc)
    content_themes = _extract_content_themes(desc)
    
    enriched = dict(row)
    enriched['email'] = email
    enriched['website'] = website
    enriched['engagement_rate'] = engagement_rate
    enriched['niche'] = niche
    enriched['content_themes'] = content_themes
    
    return enriched

def enrich_all(df):
    """Enrich all influencers in DataFrame."""
    enriched_rows = []
    for idx, row in df.iterrows():
        enriched = enrich_profile(row)
        if enriched.get('filter_status') != 'Passed':
            enriched['email'] = 'Not Found'
        enriched_rows.append(enriched)
        
    res_df = pd.DataFrame(enriched_rows)
    
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "enriched_influencers.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    res_df.to_csv(path, index=False)
    print(f"Enriched data saved to {path}")
    
    return res_df
