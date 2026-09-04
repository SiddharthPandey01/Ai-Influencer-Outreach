import os
import sys
import pandas as pd
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MIN_FOLLOWERS = 5000
MAX_FOLLOWERS = 100000

TECH_KEYWORDS = ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural', 'nlp', 'natural language', 'computer vision', 'data science', 'python', 'llm', 'large language', 'gpt', 'generative', 'transformer', 'rag', 'retrieval', 'langchain', 'embedding', 'chatbot', 'automation', 'coding', 'programming', 'developer', 'tech', 'algorithm', 'model', 'training', 'fine-tuning', 'prompt', 'api']

def clean_data(df):
    """Clean the raw DataFrame."""
    try:
        # 1. Drop duplicates by profile_url
        df = df.drop_duplicates(subset=['profile_url'])
        
        # 2. Drop rows missing name or profile_url
        df = df.dropna(subset=['name', 'profile_url'])
        
        # 3. Convert followers to int
        def parse_followers(f):
            if pd.isna(f): return 0
            if isinstance(f, (int, float)): return int(f)
            f_str = str(f).upper().replace(',', '').strip()
            if 'K' in f_str:
                return int(float(f_str.replace('K', '')) * 1000)
            if 'M' in f_str:
                return int(float(f_str.replace('M', '')) * 1000000)
            try:
                return int(float(f_str))
            except:
                return 0
                
        df['followers'] = df['followers'].apply(parse_followers)
        
        # 4. Fill missing description with 'Not Found'
        df['description'] = df['description'].fillna('Not Found')
        
        # 5. Standardize platform names
        if 'platform' in df.columns:
            df['platform'] = df['platform'].apply(lambda x: str(x).capitalize() if pd.notna(x) else 'Youtube')
        
        # 6. Remove rows with invalid URLs
        df = df[df['profile_url'].astype(str).str.startswith('http', na=False)]
        
        return df.reset_index(drop=True)
    except Exception as e:
        print(f"Error cleaning data: {e}")
        return df

def _calculate_niche_relevance(description):
    """Score 0-25 based on how many tech keywords appear in the description."""
    desc_lower = str(description).lower()
    matches = sum(1 for kw in TECH_KEYWORDS if kw in desc_lower)
    score = min(matches * 5, 25)
    return score

def _calculate_follower_fit(followers):
    """Score 0-20."""
    try:
        f = int(followers)
        if 10000 <= f <= 50000:
            return 20
        elif (5000 <= f < 10000) or (50000 < f <= 100000):
            return 15
        else:
            return 0
    except:
        return 0

def _calculate_engagement_score(row):
    """Score 0-25 based on view_count / followers ratio."""
    try:
        view_count = float(row.get('view_count', 0))
        followers = float(row.get('followers', 0))
        video_count = float(row.get('video_count', 0))
        
        if pd.isna(view_count) or pd.isna(followers) or followers == 0:
            return 0
            
        ratio = 0
        if video_count > 0:
            ratio = view_count / (followers * video_count)
            
        if ratio > 5: return 25
        elif ratio > 3: return 20
        elif ratio > 1: return 15
        elif ratio > 0.5: return 10
        else: return 5
    except:
        return 0

def _calculate_content_relevance(description):
    """Score 0-20 based on specificity of tech content."""
    desc_lower = str(description).lower()
    score = 0
    ai_specific = ['llm', 'gpt', 'rag', 'langchain', 'transformer']
    for term in ai_specific:
        if term in desc_lower:
            score += 4
    return min(score, 20)

def _calculate_profile_completeness(row):
    """Score 0-10."""
    score = 0
    desc = str(row.get('description', ''))
    if desc and desc != 'Not Found':
        score += 3
        if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', desc):
            score += 4
            
    try:
        if int(row.get('video_count', 0)) > 10:
            score += 3
    except:
        pass
    return min(score, 10)

def calculate_score(row):
    """Calculate total score (0-100)."""
    follower_fit = _calculate_follower_fit(row.get('followers', 0))
    engagement = _calculate_engagement_score(row)
    niche_relevance = _calculate_niche_relevance(row.get('description', ''))
    content_relevance = _calculate_content_relevance(row.get('description', ''))
    profile_completeness = _calculate_profile_completeness(row)
    
    total = follower_fit + engagement + niche_relevance + content_relevance + profile_completeness
    
    if total >= 80:
        classification = 'Excellent'
    elif total >= 60:
        classification = 'Good'
    elif total >= 40:
        classification = 'Review'
    else:
        classification = 'Reject'
        
    breakdown = {
        'follower_fit': follower_fit,
        'engagement': engagement,
        'niche_relevance': niche_relevance,
        'content_relevance': content_relevance,
        'profile_completeness': profile_completeness
    }
    
    return total, classification, breakdown

def filter_influencers(df):
    """Main filtering function."""
    df = clean_data(df)
    
    statuses = []
    reasons = []
    scores = []
    classifications = []
    
    for idx, row in df.iterrows():
        try:
            f = int(row['followers'])
            desc = str(row['description']).lower()
            
            has_tech = any(kw in desc for kw in TECH_KEYWORDS)
            
            if f < MIN_FOLLOWERS:
                statuses.append('Rejected')
                reasons.append('Below minimum follower range (5,000)')
            elif f > MAX_FOLLOWERS:
                statuses.append('Rejected')
                reasons.append('Above micro-influencer range (100,000)')
            elif not has_tech:
                statuses.append('Rejected')
                reasons.append('Content not relevant to technology/AI niche')
            else:
                statuses.append('Passed')
                reasons.append('Meets micro-influencer criteria')
                
            score, cls, _ = calculate_score(row)
            scores.append(score)
            classifications.append(cls)
        except Exception as e:
            statuses.append('Rejected')
            reasons.append(f'Error processing: {str(e)}')
            scores.append(0)
            classifications.append('Reject')
            
    df['filter_status'] = statuses
    df['filter_reason'] = reasons
    df['score'] = scores
    df['classification'] = classifications
    
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "enriched_influencers.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Filtered data saved to {path}")
    
    return df
