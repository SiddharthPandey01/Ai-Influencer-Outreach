"""
AI Personalization module for the AI Influencer Outreach System.

Supported AI backends (all free-tier):
  1. Google Gemini 1.5 Flash  — pass api_key='YOUR_GEMINI_KEY'
  2. Hugging Face Inference API (Mistral-7B-Instruct)  — pass hf_api_key='YOUR_HF_KEY'
  3. Template fallback  — used automatically when no API key is provided

The system auto-detects which backend to use based on which key is supplied.
"""
import os
import json
import re
import time
import hashlib
import pandas as pd
from dotenv import load_dotenv


# ─────────────────────────────────────────────────────────────
# Prompt Template Loading
# ─────────────────────────────────────────────────────────────

def _load_prompt_template(section_name):
    """
    Load a specific section from prompts/outreach_prompt.txt.
    Sections are separated by '=== SECTION_NAME ===' markers.
    """
    prompt_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'prompts', 'outreach_prompt.txt'
    )
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by === markers and find the right section
        sections = re.split(r'===\s*(.+?)\s*===', content)
        for i in range(1, len(sections), 2):
            if section_name.upper() in sections[i].upper():
                return sections[i + 1].strip() if i + 1 < len(sections) else ""
    except FileNotFoundError:
        print("Warning: prompts/outreach_prompt.txt not found. Using fallback templates.")
    return ""


# ─────────────────────────────────────────────────────────────
# Gemini API Call
# ─────────────────────────────────────────────────────────────

def _call_gemini(prompt, api_key):
    """
    Call Google Gemini 1.5 Flash (free tier).
    Get key: https://aistudio.google.com/apikey
    """
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"  Gemini API error: {e}. Retrying in 2s...")
        time.sleep(2)
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e2:
            print(f"  Gemini API retry failed: {e2}")
            return ""


# ─────────────────────────────────────────────────────────────
# Hugging Face Inference API Call
# ─────────────────────────────────────────────────────────────

# Default model — free, fast, good at following instructions
_HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"

def _call_huggingface(prompt, hf_api_key, model=None):
    """
    Call Hugging Face Inference API (free tier: 1,000 req/day).
    Uses Mistral-7B-Instruct by default — no GPU required.

    Get your free key: https://huggingface.co/settings/tokens
    Create a token with 'Read' scope (or 'Inference' scope).
    """
    import urllib.request
    import json as _json

    model_id = model or _HF_MODEL
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"

    # Format as chat instruction (Mistral instruct format)
    formatted_prompt = f"[INST] {prompt.strip()} [/INST]"

    payload = _json.dumps({
        "inputs": formatted_prompt,
        "parameters": {
            "max_new_tokens": 400,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
            "return_full_text": False,
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        api_url,
        data=payload,
        headers={
            "Authorization": f"Bearer {hf_api_key}",
            "Content-Type": "application/json",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = _json.loads(resp.read().decode("utf-8"))
            if isinstance(result, list) and result:
                return result[0].get("generated_text", "").strip()
            elif isinstance(result, dict):
                # Model may still be loading
                if "error" in result:
                    err = result["error"]
                    if "loading" in str(err).lower():
                        wait = result.get("estimated_time", 20)
                        print(f"  HF model loading, waiting {wait:.0f}s...")
                        time.sleep(min(float(wait), 30))
                        # One retry after model loads
                        with urllib.request.urlopen(
                            urllib.request.Request(
                                api_url, data=payload,
                                headers={"Authorization": f"Bearer {hf_api_key}",
                                         "Content-Type": "application/json"},
                                method="POST"
                            ), timeout=45
                        ) as resp2:
                            result2 = _json.loads(resp2.read().decode("utf-8"))
                            if isinstance(result2, list) and result2:
                                return result2[0].get("generated_text", "").strip()
                    print(f"  HF API error: {err}")
            return ""
    except Exception as e:
        print(f"  HuggingFace API error: {e}")
        return ""


# ─────────────────────────────────────────────────────────────
# Unified LLM Router
# ─────────────────────────────────────────────────────────────

def _call_llm(prompt, api_key=None, hf_api_key=None):
    """
    Route to the best available AI backend:
      1. Gemini (if api_key provided)
      2. Hugging Face (if hf_api_key provided)
      3. Returns '' so caller falls back to templates
    """
    if api_key:
        result = _call_gemini(prompt, api_key)
        if result:
            return result, "gemini"
    if hf_api_key:
        result = _call_huggingface(prompt, hf_api_key)
        if result:
            return result, "huggingface"
    return "", "template"


# ─────────────────────────────────────────────────────────────
# Template Fallback — Content Analysis
# ─────────────────────────────────────────────────────────────

def _template_fallback_analysis(influencer):
    """
    Generate content analysis WITHOUT LLM (template-based fallback).
    Derives niche, themes, tone, audience from the description.
    """
    desc = str(influencer.get('description', '')).lower()
    name = str(influencer.get('name', 'Creator'))

    # Determine niche with priority
    if any(kw in desc for kw in ['generative ai', 'gen ai', 'stable diffusion', 'midjourney']):
        niche = "Generative AI"
    elif any(kw in desc for kw in ['llm', 'large language', 'gpt', 'chatgpt', 'claude']):
        niche = "Large Language Models"
    elif any(kw in desc for kw in ['rag', 'retrieval', 'vector', 'embedding']):
        niche = "RAG & Vector Systems"
    elif any(kw in desc for kw in ['langchain', 'agent', 'chain']):
        niche = "AI Agent Frameworks"
    elif any(kw in desc for kw in ['deep learning', 'neural network', 'tensorflow', 'pytorch']):
        niche = "Deep Learning"
    elif any(kw in desc for kw in ['machine learning', 'ml', 'scikit']):
        niche = "Machine Learning"
    elif any(kw in desc for kw in ['nlp', 'natural language', 'text', 'sentiment']):
        niche = "Natural Language Processing"
    elif any(kw in desc for kw in ['computer vision', 'image', 'object detection']):
        niche = "Computer Vision"
    elif any(kw in desc for kw in ['data science', 'data analysis', 'pandas']):
        niche = "Data Science"
    elif any(kw in desc for kw in ['python', 'coding', 'programming']):
        niche = "Python Development"
    elif any(kw in desc for kw in ['ai', 'artificial intelligence']):
        niche = "Artificial Intelligence"
    elif any(kw in desc for kw in ['mlops', 'deployment', 'production']):
        niche = "MLOps"
    else:
        niche = "Technology"

    # Extract content themes
    themes = []
    theme_map = {
        'llm': 'Large Language Models', 'gpt': 'GPT Applications',
        'rag': 'RAG Pipelines', 'langchain': 'LangChain',
        'deep learning': 'Deep Learning', 'neural': 'Neural Networks',
        'nlp': 'NLP', 'computer vision': 'Computer Vision',
        'transformer': 'Transformers', 'fine-tuning': 'Model Fine-tuning',
        'prompt': 'Prompt Engineering', 'embedding': 'Embeddings',
        'python': 'Python Programming', 'api': 'API Development',
        'tutorial': 'Tutorials', 'mlops': 'MLOps',
        'data science': 'Data Science', 'machine learning': 'Machine Learning',
        'stable diffusion': 'Image Generation', 'chatbot': 'Chatbots',
        'vector': 'Vector Databases', 'deployment': 'Model Deployment'
    }
    for keyword, theme in theme_map.items():
        if keyword in desc and theme not in themes:
            themes.append(theme)
    if not themes:
        themes = ['AI Technology', 'Tech Tutorials']
    themes = themes[:5]

    # Determine tone
    if any(kw in desc for kw in ['tutorial', 'learn', 'course', 'beginner', 'explain']):
        tone = "Educational"
    elif any(kw in desc for kw in ['review', 'compare', 'best', 'tool']):
        tone = "Analytical"
    elif any(kw in desc for kw in ['build', 'project', 'hands-on', 'practical']):
        tone = "Hands-on"
    elif any(kw in desc for kw in ['research', 'paper', 'breakthrough']):
        tone = "Research-focused"
    else:
        tone = "Educational"

    # Derive audience
    audience_map = {
        "Generative AI": "AI enthusiasts and creative technologists",
        "Large Language Models": "AI developers and LLM practitioners",
        "RAG & Vector Systems": "AI engineers building search and retrieval systems",
        "AI Agent Frameworks": "developers building autonomous AI agents",
        "Deep Learning": "ML engineers and AI researchers",
        "Machine Learning": "data scientists and ML practitioners",
        "Natural Language Processing": "NLP engineers and text analytics developers",
        "Computer Vision": "CV engineers and image processing developers",
        "Data Science": "aspiring data scientists and analysts",
        "Python Development": "Python developers and programmers",
        "MLOps": "ML engineers focused on production systems",
    }
    audience = audience_map.get(niche, f"tech professionals interested in {niche}")

    # Collaboration angle
    angle_map = {
        "Generative AI": "AI creative tool sponsorship or co-created content",
        "Large Language Models": "LLM platform or API tool integration demo",
        "RAG & Vector Systems": "vector database or retrieval tool partnership",
        "Deep Learning": "GPU/compute platform or framework sponsorship",
        "Machine Learning": "ML platform or AutoML tool collaboration",
        "Data Science": "data tool or analytics platform review",
        "Python Development": "developer tool or IDE sponsorship",
    }
    collaboration_angle = angle_map.get(niche, f"sponsored content featuring AI developer tools")

    return {
        "niche": niche,
        "content_themes": themes,
        "tone": tone,
        "audience": audience,
        "collaboration_angle": collaboration_angle
    }


# ─────────────────────────────────────────────────────────────
# Template Fallback — Email (60-90 words each, 5 varied templates)
# ─────────────────────────────────────────────────────────────

def _template_fallback_email(influencer, analysis):
    """
    Generate a personalized email WITHOUT LLM.
    Each email is 60-90 words, unique per influencer.
    """
    name = influencer.get('name', 'Creator')
    niche = analysis.get('niche', 'AI technology')
    themes = analysis.get('content_themes', ['AI technology'])
    theme = themes[0] if themes else 'AI technology'
    theme2 = themes[1] if len(themes) > 1 else theme
    audience = analysis.get('audience', 'your audience')
    tone = analysis.get('tone', 'Educational')
    followers = influencer.get('followers', 1000)
    followers_k = round(int(followers) / 1000, 1) if isinstance(followers, (int, float)) else 10
    collab = analysis.get('collaboration_angle', 'a sponsored content partnership')

    templates = [
        f"Hi {name},\n\nI've been following your {niche} content on YouTube, particularly your excellent coverage of {theme}. Your {tone.lower()} approach makes complex topics accessible to {audience}, and that's exactly what drew us in. Our team is building next-generation AI developer tools, and we believe a collaboration could provide real value to your {followers_k}K subscribers. Would you be open to discussing {collab}? We'd love to explore how we can work together.\n\nBest regards",

        f"Hi {name},\n\nYour deep dives into {theme} and {theme2} on YouTube are consistently impressive. The way you engage {audience} through your {tone.lower()} style sets your channel apart. We're developing cutting-edge AI tools for developers and think your community of {followers_k}K subscribers would genuinely benefit from seeing them in action. Could we set up a quick call to discuss a potential {collab}? Looking forward to hearing your thoughts.\n\nCheers",

        f"Hi {name},\n\nI recently came across your {niche} channel and was impressed by your content on {theme}. Your ability to break down {theme2} for {audience} is truly exceptional. We're a team working on innovative AI developer tools, and your {followers_k}K-strong community seems like a perfect match. We'd love to explore {collab} with you — something that adds real value to your viewers while showcasing our platform.\n\nWould you be interested in chatting further?\n\nBest",

        f"Hi {name},\n\nAs someone deeply invested in the {niche} space, I've found your YouTube content on {theme} both insightful and engaging. Your {tone.lower()} style resonates with {audience}, which is why we think you'd be a great partner. Our startup is focused on AI developer productivity tools, and we see a strong fit with your {followers_k}K audience. Let's discuss {collab} that benefits both your viewers and our platform.\n\nLooking forward to connecting",

        f"Hi {name},\n\nYour {niche} YouTube channel caught our attention, especially your work covering {theme}. The quality of content you deliver to {audience} is remarkable, and your {tone.lower()} presentation style makes everything engaging. Our team builds AI tools for developers and we're looking for authentic creators with audiences like your {followers_k}K subscribers. We'd love to discuss {collab}. Are you available for a brief conversation this week?\n\nWarm regards"
    ]

    # Select template based on name hash for consistent but varied selection
    idx = int(hashlib.md5(name.encode()).hexdigest(), 16) % len(templates)
    return templates[idx]


# ─────────────────────────────────────────────────────────────
# Template Fallback — Instagram DM (15-30 words each, 5 varied templates)
# ─────────────────────────────────────────────────────────────

def _template_fallback_dm(influencer, analysis):
    """
    Generate a personalized Instagram DM WITHOUT LLM.
    Each DM is 15-30 words, unique per influencer.
    """
    name = influencer.get('name', 'there')
    themes = analysis.get('content_themes', ['AI technology'])
    theme = themes[0] if themes else 'AI technology'
    niche = analysis.get('niche', 'tech')

    templates = [
        f"Hi {name}! Your {theme} content is fantastic. We build AI dev tools and would love to explore a collaboration with you. Interested?",
        f"Hey {name}, really enjoying your {niche} tutorials! Your take on {theme} is spot-on. Would you be open to a sponsored partnership?",
        f"Hi {name}! Big fan of your work on {theme}. We're developing AI tools that align perfectly with your content. Open to a collab?",
        f"Love your {theme} videos, {name}! Your {niche} expertise really shines through. We'd love to discuss a content partnership with you.",
        f"Hi {name}, your {niche} content on {theme} is impressive! Our AI tools team thinks a collaboration could be amazing. Let's connect!"
    ]

    idx = int(hashlib.md5(name.encode()).hexdigest(), 16) % len(templates)
    return templates[idx]


# ─────────────────────────────────────────────────────────────
# Main Functions
# ─────────────────────────────────────────────────────────────

def analyze_content(influencer, api_key=None, hf_api_key=None):
    """
    Analyze influencer content using Gemini, HuggingFace, or template fallback.
    Returns: dict with niche, content_themes, tone, audience, collaboration_angle
    """
    if not api_key and not hf_api_key:
        return _template_fallback_analysis(influencer)

    template = _load_prompt_template('CONTENT ANALYSIS PROMPT')
    if not template:
        return _template_fallback_analysis(influencer)

    prompt = template.replace('{name}', str(influencer.get('name', '')))
    prompt = prompt.replace('{platform}', str(influencer.get('platform', 'YouTube')))
    prompt = prompt.replace('{followers}', str(influencer.get('followers', '')))
    prompt = prompt.replace('{description}', str(influencer.get('description', '')))
    prompt = prompt.replace('{recent_videos}', 'Not available')

    response, backend = _call_llm(prompt, api_key=api_key, hf_api_key=hf_api_key)
    if response:
        try:
            cleaned = re.sub(r'```json\s*', '', response)
            cleaned = re.sub(r'```\s*', '', cleaned)
            return json.loads(cleaned.strip())
        except json.JSONDecodeError:
            print(f"  Warning: Could not parse {backend} JSON response, using fallback")

    return _template_fallback_analysis(influencer)


def generate_email(influencer, analysis, api_key=None, hf_api_key=None):
    """
    Generate a 60-90 word personalized email.
    Uses Gemini, HuggingFace, or template fallback automatically.
    """
    template = _load_prompt_template('EMAIL GENERATION PROMPT')
    if not template or (not api_key and not hf_api_key):
        return _template_fallback_email(influencer, analysis)

    themes = analysis.get('content_themes', ['AI'])
    themes_str = ', '.join(themes) if isinstance(themes, list) else str(themes)

    prompt = template.replace('{name}', str(influencer.get('name', '')))
    prompt = prompt.replace('{platform}', str(influencer.get('platform', 'YouTube')))
    prompt = prompt.replace('{followers}', str(influencer.get('followers', '')))
    prompt = prompt.replace('{niche}', str(analysis.get('niche', '')))
    prompt = prompt.replace('{content_themes}', themes_str)
    prompt = prompt.replace('{tone}', str(analysis.get('tone', '')))
    prompt = prompt.replace('{audience}', str(analysis.get('audience', '')))
    prompt = prompt.replace('{recent_videos}', 'Not available')
    prompt = prompt.replace('{collaboration_angle}', str(analysis.get('collaboration_angle', '')))

    response, _ = _call_llm(prompt, api_key=api_key, hf_api_key=hf_api_key)
    if response:
        response = response.strip()
        words = response.split()
        if 55 <= len(words) <= 100:
            return response

    return _template_fallback_email(influencer, analysis)


def generate_dm(influencer, analysis, api_key=None, hf_api_key=None):
    """
    Generate a 15-30 word personalized Instagram DM.
    Uses Gemini, HuggingFace, or template fallback automatically.
    """
    template = _load_prompt_template('DM GENERATION PROMPT')
    if not template or (not api_key and not hf_api_key):
        return _template_fallback_dm(influencer, analysis)

    themes = analysis.get('content_themes', ['AI'])
    themes_str = ', '.join(themes) if isinstance(themes, list) else str(themes)

    prompt = template.replace('{name}', str(influencer.get('name', '')))
    prompt = prompt.replace('{niche}', str(analysis.get('niche', '')))
    prompt = prompt.replace('{content_themes}', themes_str)
    prompt = prompt.replace('{recent_videos}', 'Not available')

    response, _ = _call_llm(prompt, api_key=api_key, hf_api_key=hf_api_key)
    if response:
        response = response.strip()
        words = response.split()
        if 12 <= len(words) <= 35:
            return response

    return _template_fallback_dm(influencer, analysis)


def personalize_all(df, api_key=None, hf_api_key=None):
    """
    Run personalization for all qualified influencers.
    Only processes rows where filter_status == 'Passed'.

    AI backend priority:
      1. Gemini (api_key)
      2. Hugging Face (hf_api_key)
      3. Template fallback

    Returns DataFrame with added columns: content_analysis, email_pitch, instagram_dm
    """
    df = df.copy()

    if 'content_analysis' not in df.columns:
        df['content_analysis'] = ""
    if 'email_pitch' not in df.columns:
        df['email_pitch'] = ""
    if 'instagram_dm' not in df.columns:
        df['instagram_dm'] = ""

    qualified_mask = df['filter_status'] == 'Passed' if 'filter_status' in df.columns else pd.Series([True] * len(df))
    total_qualified = qualified_mask.sum()
    current = 0

    if api_key:
        mode = "Google Gemini 1.5 Flash"
    elif hf_api_key:
        mode = f"HuggingFace ({_HF_MODEL})"
    else:
        mode = "Template fallback (no API key)"

    print(f"\n{'=' * 50}")
    print(f"\U0001f916 Starting personalization — {mode}")
    print(f"   Qualified influencers: {total_qualified}")
    print(f"{'=' * 50}")

    for idx, row in df.iterrows():
        if qualified_mask.loc[idx]:
            current += 1
            name = row.get('name', 'Unknown')
            print(f"\nPersonalizing {current}/{total_qualified}: {name}...")

            try:
                influencer = row.to_dict()

                analysis = analyze_content(influencer, api_key=api_key, hf_api_key=hf_api_key)
                print(f"  \u2713 Content analysis: {analysis.get('niche', 'N/A')}")

                email = generate_email(influencer, analysis, api_key=api_key, hf_api_key=hf_api_key)
                print(f"  \u2713 Email: {len(email.split())} words")

                dm = generate_dm(influencer, analysis, api_key=api_key, hf_api_key=hf_api_key)
                print(f"  \u2713 DM: {len(dm.split())} words")

                df.at[idx, 'content_analysis'] = json.dumps(analysis)
                df.at[idx, 'email_pitch'] = email
                df.at[idx, 'instagram_dm'] = dm

                # Rate limiting for live API calls
                if api_key or hf_api_key:
                    time.sleep(1)

            except Exception as e:
                print(f"  \u2717 Error personalizing {name}: {str(e)}")
                df.at[idx, 'content_analysis'] = json.dumps({"error": str(e)})
                df.at[idx, 'email_pitch'] = ""
                df.at[idx, 'instagram_dm'] = ""
        else:
            df.at[idx, 'content_analysis'] = ""
            df.at[idx, 'email_pitch'] = ""
            df.at[idx, 'instagram_dm'] = ""

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'enriched_influencers.csv')
    df.to_csv(out_path, index=False)

    print(f"\n{'=' * 50}")
    print(f"\u2705 Personalization complete! ({current} influencers processed)")
    print(f"   Saved to: {out_path}")
    print(f"{'=' * 50}")

    return df
