"""
fetch_real_data.py  —  One-time script to fetch REAL YouTube channel data.

Run this once with your YouTube Data API key:
    python fetch_real_data.py --api-key YOUR_KEY_HERE

Or set YOUTUBE_API_KEY in your .env file and just run:
    python fetch_real_data.py

This saves real influencer data to:
    data/raw_influencers.csv

The Streamlit app + sample_data.py will automatically prefer
this file over synthetic records.

YouTube Data API v3 is FREE: 10,000 units/day quota.
Each search costs ~100 units, each channels.list costs ~1 unit per channel.
This script uses approx. 1,200 units total (well within the daily free quota).

Get your free API key at:
    https://console.cloud.google.com/ → APIs & Services → YouTube Data API v3
"""

import os
import sys
import json
import time
import argparse
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# Search terms targeting AI / Machine Learning / Python micro-influencers
# ─────────────────────────────────────────────────────────────────────────────
SEARCH_TERMS = [
    "LangChain tutorial Python",
    "RAG tutorial AI",
    "LLM fine tuning tutorial",
    "Generative AI projects Python",
    "OpenAI API tutorial",
    "machine learning project tutorial",
    "Hugging Face transformers tutorial",
    "AI agents Python tutorial",
    "vector database tutorial Python",
    "deep learning beginner tutorial",
    "ChatGPT API Python project",
    "AI automation Python",
    "data science Python tutorial",
    "PyTorch tutorial beginner",
    "computer vision OpenCV Python",
]

# Subscriber range for micro-influencers
MIN_SUBS = 1_000    # fetch a bit below target to show filtering working
MAX_SUBS = 500_000  # fetch a bit above target too

OUTPUT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw_influencers.csv")


def fetch_channels(api_key: str, max_per_term: int = 10) -> list[dict]:
    """
    Search YouTube for channels matching SEARCH_TERMS, then pull full
    channel stats. Returns a deduplicated list of channel dicts.
    """
    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
    except ImportError:
        print("ERROR: google-api-python-client not installed.")
        print("Run:  pip install google-api-python-client")
        sys.exit(1)

    youtube = build("youtube", "v3", developerKey=api_key)
    seen_ids: set[str] = set()
    channel_ids_all: list[str] = []

    print(f"\n{'='*60}")
    print(" Searching YouTube for AI/ML channels...")
    print(f"{'='*60}")

    for term in SEARCH_TERMS:
        print(f"  Searching: '{term}'")
        try:
            resp = youtube.search().list(
                q=term,
                type="channel",
                part="id",
                maxResults=max_per_term,
                relevanceLanguage="en",
            ).execute()

            for item in resp.get("items", []):
                cid = item["id"]["channelId"]
                if cid not in seen_ids:
                    seen_ids.add(cid)
                    channel_ids_all.append(cid)

            time.sleep(0.3)   # be gentle with the API
        except Exception as e:
            print(f"    WARNING: Search failed for '{term}': {e}")

    print(f"\n  Found {len(channel_ids_all)} unique channels. Fetching stats...\n")

    # Fetch stats in batches of 50 (API limit per request)
    influencers: list[dict] = []
    batch_size = 50
    for i in range(0, len(channel_ids_all), batch_size):
        batch = channel_ids_all[i : i + batch_size]
        try:
            resp = youtube.channels().list(
                id=",".join(batch),
                part="snippet,statistics,brandingSettings",
            ).execute()

            for ch in resp.get("items", []):
                snippet = ch.get("snippet", {})
                stats = ch.get("statistics", {})
                branding = ch.get("brandingSettings", {}).get("channel", {})

                subs = int(stats.get("subscriberCount", 0))
                videos = int(stats.get("videoCount", 0))
                views = int(stats.get("viewCount", 0))

                # Skip channels with hidden subscriber counts or very few videos
                if stats.get("hiddenSubscriberCount", False):
                    continue
                if videos < 5:
                    continue

                description = snippet.get("description", "")
                name = snippet.get("title", "Unknown")
                cid = ch["id"]

                influencers.append({
                    "name": name,
                    "platform": "YouTube",
                    "profile_url": f"https://youtube.com/channel/{cid}",
                    "channel_id": cid,
                    "followers": subs,
                    "description": description[:2000],   # truncate for DB
                    "video_count": videos,
                    "view_count": views,
                    "country": snippet.get("country", ""),
                    "published_at": snippet.get("publishedAt", ""),
                    "keywords": branding.get("keywords", ""),
                    "data_source": "YouTube Data API v3",
                })

        except Exception as e:
            print(f"    WARNING: channels.list batch failed: {e}")
        time.sleep(0.3)

    return influencers


def save_results(influencers: list[dict]) -> str:
    df = pd.DataFrame(influencers)
    df.drop_duplicates(subset=["channel_id"], inplace=True)
    df.sort_values("followers", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    return OUTPUT_CSV


def print_summary(df: pd.DataFrame):
    micro = df[(df["followers"] >= 5_000) & (df["followers"] <= 100_000)]
    below = df[df["followers"] < 5_000]
    above = df[df["followers"] > 100_000]

    print(f"\n{'='*60}")
    print(" RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"  Total channels fetched   : {len(df)}")
    print(f"  Micro-influencers (5K-100K): {len(micro)}")
    print(f"  Below range (<5K)          : {len(below)}")
    print(f"  Above range (>100K)        : {len(above)}")
    print(f"\n  Sample micro-influencers found:")
    for _, row in micro.head(10).iterrows():
        print(f"    • {row['name']:<35} {row['followers']:>8,} subs")
    print(f"\n  Saved to: {OUTPUT_CSV}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch real YouTube AI/ML channel data for the influencer outreach system."
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.getenv("YOUTUBE_API_KEY", ""),
        help="Your YouTube Data API v3 key (or set YOUTUBE_API_KEY in .env)",
    )
    parser.add_argument(
        "--max-per-term",
        type=int,
        default=10,
        help="Max channels to fetch per search term (default: 10)",
    )
    args = parser.parse_args()

    if not args.api_key:
        print("\nERROR: No YouTube API key provided.")
        print("Options:")
        print("  1. Add YOUTUBE_API_KEY=your_key to your .env file")
        print("  2. Pass it as: python fetch_real_data.py --api-key YOUR_KEY")
        print("\nGet a FREE key at: https://console.cloud.google.com/")
        print("  → APIs & Services → Enable 'YouTube Data API v3' → Credentials → Create API Key")
        print("\nFree quota: 10,000 units/day  |  This script uses ~1,200 units\n")
        sys.exit(1)

    print(f"\nUsing API key: {args.api_key[:8]}{'*' * (len(args.api_key) - 8)}")

    influencers = fetch_channels(args.api_key, max_per_term=args.max_per_term)

    if not influencers:
        print("\nERROR: No channels were fetched. Check your API key and quota.")
        sys.exit(1)

    path = save_results(influencers)
    df = pd.read_csv(path)
    print_summary(df)

    print("SUCCESS! Now launch the Streamlit dashboard:")
    print("    streamlit run app.py")
    print("Click 'Run Discovery' — it will load from the real data file.\n")


if __name__ == "__main__":
    main()
