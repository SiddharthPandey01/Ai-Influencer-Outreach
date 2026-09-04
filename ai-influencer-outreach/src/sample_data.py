"""
sample_data.py  —  Data provider for the AI Influencer Outreach System.

Priority order:
  1. data/raw_influencers.csv  — real YouTube API data (if fetch_real_data.py was run)
  2. Synthetic fallback         — clearly labelled fake records for demo purposes only

The assignment requires real data. Run:
    python fetch_real_data.py --api-key YOUR_YOUTUBE_KEY
to populate the CSV with genuine YouTube channel data.
"""

import os
import pandas as pd

# Path to the real data file produced by fetch_real_data.py
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REAL_CSV = os.path.join(_ROOT, "data", "raw_influencers.csv")

# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def get_sample_influencers() -> list[dict]:
    """
    Return influencer records as a list of dicts.

    If real YouTube API data exists in data/raw_influencers.csv, load that.
    Otherwise return clearly-labelled synthetic fallback records (demo only).
    """
    if os.path.exists(_REAL_CSV):
        df = pd.read_csv(_REAL_CSV)
        # Ensure required columns exist
        required = ["name", "platform", "profile_url", "channel_id",
                    "followers", "description", "video_count", "view_count"]
        for col in required:
            if col not in df.columns:
                df[col] = "" if col in ("name", "platform", "profile_url",
                                         "channel_id", "description") else 0
        df["platform"] = df["platform"].fillna("YouTube")
        df["description"] = df["description"].fillna("")
        df["followers"] = pd.to_numeric(df["followers"], errors="coerce").fillna(0).astype(int)
        df["video_count"] = pd.to_numeric(df["video_count"], errors="coerce").fillna(0).astype(int)
        df["view_count"] = pd.to_numeric(df["view_count"], errors="coerce").fillna(0).astype(int)
        records = df[required].to_dict("records")
        print(f"[sample_data] Loaded {len(records)} REAL records from {_REAL_CSV}")
        return records

    # ── Fallback: synthetic data ─────────────────────────────────────────────
    print("[sample_data] WARNING: No real data found. Using SYNTHETIC fallback.")
    print(f"[sample_data] Run:  python fetch_real_data.py --api-key YOUR_KEY")
    return _synthetic_fallback()


def real_data_available() -> bool:
    """Return True if a real YouTube data CSV has been fetched."""
    return os.path.exists(_REAL_CSV)


# ─────────────────────────────────────────────────────────────────────────────
# Synthetic fallback — clearly labelled, for demo/testing purposes only
# ─────────────────────────────────────────────────────────────────────────────

def _synthetic_fallback() -> list[dict]:
    """
    55 synthetic YouTube channel records.

    IMPORTANT: These are NOT real channels. Names, URLs, channel IDs,
    subscriber counts and email addresses are entirely fabricated.
    This data is ONLY for testing the pipeline logic when no real data exists.
    Do NOT submit this as evidence of real influencer discovery.

    Distribution:
      - 10 creators with <5,000 subs  → will be REJECTED (below micro range)
      - 30 creators with 5K–100K subs → PASS (micro-influencers)
      - 15 creators with >100K subs   → will be REJECTED (above micro range)
    """
    return [
        # ── GROUP 1: <5,000 subs — REJECTED ──────────────────────────────────
        {
            "name": "[SYNTHETIC] CodeNewbie AI",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@CodeNewbieAI_FAKE",
            "channel_id": "FAKE_UCxN3kR7a9Qj2mP4bW1cYdEf",
            "followers": 1200,
            "description": "SYNTHETIC TEST RECORD. Just starting my journey into artificial intelligence and Python programming.",
            "video_count": 24,
            "view_count": 18000,
        },
        {
            "name": "[SYNTHETIC] TinyML Studio",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@TinyMLStudio_FAKE",
            "channel_id": "FAKE_UCyK4pR8s1Tj3nQ5bW2dYeGh",
            "followers": 890,
            "description": "SYNTHETIC TEST RECORD. Exploring TinyML and edge AI deployments on microcontrollers.",
            "video_count": 31,
            "view_count": 12500,
        },
        {
            "name": "[SYNTHETIC] AI Sketches",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@AISketches_FAKE",
            "channel_id": "FAKE_UCzL5qR9s2Uj4mP6cX3eYfIj",
            "followers": 2300,
            "description": "SYNTHETIC TEST RECORD. Visual explanations of neural network architectures. 📧 aisketches@outlook.com",
            "video_count": 45,
            "view_count": 34000,
        },
        {
            "name": "[SYNTHETIC] PythonMicroLab",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@PythonMicroLab_FAKE",
            "channel_id": "FAKE_UCaM6pR0t3Vk5nQ7dX4fYgKl",
            "followers": 3400,
            "description": "SYNTHETIC TEST RECORD. Python micro-projects every week. Flask APIs and Pandas tutorials.",
            "video_count": 67,
            "view_count": 52000,
        },
        {
            "name": "[SYNTHETIC] NeuralByte",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@NeuralByte_FAKE",
            "channel_id": "FAKE_UCbN7qS1u4Vl6oR8eX5fZhMn",
            "followers": 780,
            "description": "SYNTHETIC TEST RECORD. Neural network fundamentals, byte-sized lessons.",
            "video_count": 19,
            "view_count": 9800,
        },
        {
            "name": "[SYNTHETIC] MLCrafter",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@MLCrafter_FAKE",
            "channel_id": "FAKE_UCcO8rT2v5Wm7pS9fY6gAhNo",
            "followers": 2900,
            "description": "SYNTHETIC TEST RECORD. Crafting machine learning models step by step. scikit-learn, XGBoost tutorials.",
            "video_count": 38,
            "view_count": 27000,
        },
        {
            "name": "[SYNTHETIC] DataDoodle",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@DataDoodle_FAKE",
            "channel_id": "FAKE_UCdP9sU3w6Xn8qT0gZ7hBiPq",
            "followers": 1650,
            "description": "SYNTHETIC TEST RECORD. Doodling through data science. Matplotlib and Seaborn visualization tutorials.",
            "video_count": 29,
            "view_count": 16000,
        },
        {
            "name": "[SYNTHETIC] AIWeekly",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@AIWeekly_FAKE",
            "channel_id": "FAKE_UCeQ0tV4x7Yo9rU1hA8iBjRr",
            "followers": 4200,
            "description": "SYNTHETIC TEST RECORD. Weekly AI news roundups and paper summaries.",
            "video_count": 84,
            "view_count": 63000,
        },
        {
            "name": "[SYNTHETIC] GPT Explorer",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@GPTExplorer_FAKE",
            "channel_id": "FAKE_UCfR1uW5y8Zp0sV2iB9jCkSs",
            "followers": 3100,
            "description": "SYNTHETIC TEST RECORD. Exploring GPT and ChatGPT for productivity. Prompt engineering tips.",
            "video_count": 42,
            "view_count": 38000,
        },
        {
            "name": "[SYNTHETIC] LlamaCoder",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@LlamaCoder_FAKE",
            "channel_id": "FAKE_UCgS2vX6z9Aq1tW3jC0kDlTt",
            "followers": 990,
            "description": "SYNTHETIC TEST RECORD. Open-source LLM tutorials: Llama, Mistral, Phi models.",
            "video_count": 15,
            "view_count": 7200,
        },

        # ── GROUP 2: 5K–100K subs — PASS (micro-influencers) ─────────────────
        {
            "name": "[SYNTHETIC] LangChain Labs",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@LangChainLabs_FAKE",
            "channel_id": "FAKE_UChT3wY7a0Br2uX4kD1lEmUu",
            "followers": 9800,
            "description": "SYNTHETIC TEST RECORD. Deep-dive LangChain tutorials: agents, LCEL, RAG pipelines. 📧 langchainlabs@gmail.com",
            "video_count": 56,
            "view_count": 320000,
        },
        {
            "name": "[SYNTHETIC] VectorDB Tutorials",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@VectorDBTutorials_FAKE",
            "channel_id": "FAKE_UCiU4xZ8b1Cs3vY5lE2mFnVv",
            "followers": 14200,
            "description": "SYNTHETIC TEST RECORD. Pinecone, Weaviate, Qdrant — practical vector database tutorials for AI apps.",
            "video_count": 41,
            "view_count": 480000,
        },
        {
            "name": "[SYNTHETIC] AI Startup Builder",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@AIStartupBuilder_FAKE",
            "channel_id": "FAKE_UCjV5yA9c2Dt4wZ6mF3nGoWw",
            "followers": 22500,
            "description": "SYNTHETIC TEST RECORD. Building AI-powered startups with Python, FastAPI, and OpenAI. 📧 info@aistartupbuilder.io",
            "video_count": 78,
            "view_count": 920000,
        },
        {
            "name": "[SYNTHETIC] HuggingFace Hero",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@HuggingFaceHero_FAKE",
            "channel_id": "FAKE_UCkW6zA0d3Eu5xA7nG4oHpXx",
            "followers": 31000,
            "description": "SYNTHETIC TEST RECORD. Hugging Face Transformers, Diffusers, and Datasets tutorials. Fine-tuning LLMs made easy.",
            "video_count": 93,
            "view_count": 1400000,
        },
        {
            "name": "[SYNTHETIC] MLOps Weekly",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@MLOpsWeekly_FAKE",
            "channel_id": "FAKE_UClX7aB1e4Fv6yB8oH5pIqYy",
            "followers": 18700,
            "description": "SYNTHETIC TEST RECORD. MLOps: model deployment, CI/CD for ML, MLflow, Kubeflow, and monitoring.",
            "video_count": 64,
            "view_count": 720000,
        },
        {
            "name": "[SYNTHETIC] PythonAI Projects",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@PythonAIProjects_FAKE",
            "channel_id": "FAKE_UCmY8bC2f5Gw7zA9pH6qJrZz",
            "followers": 7600,
            "description": "SYNTHETIC TEST RECORD. Python AI project tutorials: face recognition, NLP, recommendation systems. 📧 pythonaiprojects@hotmail.com",
            "video_count": 47,
            "view_count": 265000,
        },
        {
            "name": "[SYNTHETIC] Prompt Architect",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@PromptArchitect_FAKE",
            "channel_id": "FAKE_UCnZ9cD3g6Hx8aB0qI7rKsAa",
            "followers": 43000,
            "description": "SYNTHETIC TEST RECORD. Advanced prompt engineering for ChatGPT, Claude, and Gemini. Chain-of-thought and few-shot techniques.",
            "video_count": 110,
            "view_count": 2100000,
        },
        {
            "name": "[SYNTHETIC] DataPipeline Pro",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@DataPipelinePro_FAKE",
            "channel_id": "FAKE_UCoA0dE4h7Iy9bC1rJ8sTBb",
            "followers": 11300,
            "description": "SYNTHETIC TEST RECORD. Apache Airflow, Kafka, dbt, and Spark for production data pipelines.",
            "video_count": 55,
            "view_count": 410000,
        },
        {
            "name": "[SYNTHETIC] CV Engineer",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@CVEngineer_FAKE",
            "channel_id": "FAKE_UCpB1eF5i8Jz0cD2sK9tUCc",
            "followers": 27800,
            "description": "SYNTHETIC TEST RECORD. Computer vision engineering: YOLO, OpenCV, MediaPipe. Real-world detection projects. 📧 cvengchannel@gmail.com",
            "video_count": 82,
            "view_count": 1150000,
        },
        {
            "name": "[SYNTHETIC] AI Paper Club",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@AIPaperClub_FAKE",
            "channel_id": "FAKE_UCqC2fG6j9Ka1dE3tL0uVDd",
            "followers": 6200,
            "description": "SYNTHETIC TEST RECORD. Weekly deep-dives into the latest AI research papers. Attention, transformers, and beyond.",
            "video_count": 38,
            "view_count": 180000,
        },
        {
            "name": "[SYNTHETIC] FastAPI AI",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@FastAPIAI_FAKE",
            "channel_id": "FAKE_UCrD3gH7k0Lb2eF4uM1vWEe",
            "followers": 16400,
            "description": "SYNTHETIC TEST RECORD. Building AI REST APIs with FastAPI, Docker, and Pydantic. Production ML deployment.",
            "video_count": 61,
            "view_count": 590000,
        },
        {
            "name": "[SYNTHETIC] Streamlit Builder",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@StreamlitBuilder_FAKE",
            "channel_id": "FAKE_UCsE4hI8l1Mc3fG5vN2wXFf",
            "followers": 8900,
            "description": "SYNTHETIC TEST RECORD. Building data apps and AI dashboards with Streamlit. From prototype to production. 📧 streamlitbuilder@gmail.com",
            "video_count": 44,
            "view_count": 310000,
        },
        {
            "name": "[SYNTHETIC] NLP Decoded",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@NLPDecoded_FAKE",
            "channel_id": "FAKE_UCtF5iJ9m2Nd4gH6wO3xYGg",
            "followers": 39000,
            "description": "SYNTHETIC TEST RECORD. Natural language processing decoded: BERT, GPT, T5. Text classification, NER, and sentiment analysis.",
            "video_count": 96,
            "view_count": 1800000,
        },
        {
            "name": "[SYNTHETIC] AI Tool Reviews",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@AIToolReviews_FAKE",
            "channel_id": "FAKE_UCuG6jK0n3Oe5hI7xP4yZHh",
            "followers": 52000,
            "description": "SYNTHETIC TEST RECORD. Honest reviews of AI productivity tools: Notion AI, Copilot, Perplexity, and more.",
            "video_count": 145,
            "view_count": 3100000,
        },
        {
            "name": "[SYNTHETIC] LLM Engineer",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@LLMEngineer_FAKE",
            "channel_id": "FAKE_UCvH7kL1o4Pf6iJ8yQ5zAIi",
            "followers": 21000,
            "description": "SYNTHETIC TEST RECORD. Large Language Model engineering: from tokens to production deployment. RAG, fine-tuning, evaluation. 📧 llmengineer@proton.me",
            "video_count": 70,
            "view_count": 870000,
        },
        {
            "name": "[SYNTHETIC] AI Automation Hub",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@AIAutomationHub_FAKE",
            "channel_id": "FAKE_UCwI8lM2p5Qg7jK9zR6aBJj",
            "followers": 67000,
            "description": "SYNTHETIC TEST RECORD. Automate your business with AI: Make.com, Zapier AI, Python automation scripts.",
            "video_count": 188,
            "view_count": 4200000,
        },
        {
            "name": "[SYNTHETIC] GraphRAG Tutorials",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@GraphRAGTutorials_FAKE",
            "channel_id": "FAKE_UCxJ9mN3q6Rh8kL0aS7cCKk",
            "followers": 5400,
            "description": "SYNTHETIC TEST RECORD. Knowledge graphs meets RAG: Neo4j, GraphRAG, and structured AI retrieval tutorials.",
            "video_count": 28,
            "view_count": 142000,
        },
        {
            "name": "[SYNTHETIC] AI Ethics Watch",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@AIEthicsWatch_FAKE",
            "channel_id": "FAKE_UCyK0nO4r7Si9lM1bT8dDLl",
            "followers": 12100,
            "description": "SYNTHETIC TEST RECORD. Critical analysis of AI bias, fairness, and societal impact. Responsible AI development. 📧 aiethicswatch@substack.com",
            "video_count": 49,
            "view_count": 380000,
        },
        {
            "name": "[SYNTHETIC] CrewAI Projects",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@CrewAIProjects_FAKE",
            "channel_id": "FAKE_UCzL1oP5s8Tj0mN2cU9eEMm",
            "followers": 34000,
            "description": "SYNTHETIC TEST RECORD. Multi-agent AI systems with CrewAI and AutoGen. Build AI teams that work together.",
            "video_count": 87,
            "view_count": 1600000,
        },
        {
            "name": "[SYNTHETIC] Stable Diffusion Pro",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@StableDiffusionPro_FAKE",
            "channel_id": "FAKE_UCAm2pQ6t9Uk1nO3dV0fFNn",
            "followers": 78000,
            "description": "SYNTHETIC TEST RECORD. Mastering Stable Diffusion: ComfyUI, ControlNet, LoRA training. Image generation tutorials.",
            "video_count": 214,
            "view_count": 5800000,
        },
        {
            "name": "[SYNTHETIC] PyTorch From Scratch",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@PyTorchFromScratch_FAKE",
            "channel_id": "FAKE_UCBn3qR7u0Vl2oP4eW1gGOo",
            "followers": 15600,
            "description": "SYNTHETIC TEST RECORD. PyTorch deep learning from scratch: tensors to custom training loops. No fluff.",
            "video_count": 66,
            "view_count": 560000,
        },
        {
            "name": "[SYNTHETIC] DataOps Daily",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@DataOpsDaily_FAKE",
            "channel_id": "FAKE_UCCo4rS8v1Wm3pQ5fX2hHPp",
            "followers": 47000,
            "description": "SYNTHETIC TEST RECORD. Daily DataOps tips: dbt, Snowflake, Databricks, and the modern data stack.",
            "video_count": 132,
            "view_count": 2700000,
        },
        {
            "name": "[SYNTHETIC] Open Source AI",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@OpenSourceAI_FAKE",
            "channel_id": "FAKE_UCDp5sT9w2Xn4qR6gY3iIQq",
            "followers": 29500,
            "description": "SYNTHETIC TEST RECORD. Open-source AI tools: Ollama, LocalAI, PrivateGPT. Run AI models locally.",
            "video_count": 95,
            "view_count": 1350000,
        },
        {
            "name": "[SYNTHETIC] AI Career Coach",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@AICareerCoach_FAKE",
            "channel_id": "FAKE_UCEq6tU0x3Yo5rS7hZ4jJRr",
            "followers": 61000,
            "description": "SYNTHETIC TEST RECORD. AI career advice: ML engineer vs data scientist, portfolio projects, interview prep. 📧 aicareers@coaching.com",
            "video_count": 168,
            "view_count": 3900000,
        },
        {
            "name": "[SYNTHETIC] Gemini API Tutorials",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@GeminiAPITutorials_FAKE",
            "channel_id": "FAKE_UCFr7uV1y4Zp6sT8iA5kKSs",
            "followers": 8100,
            "description": "SYNTHETIC TEST RECORD. Google Gemini API tutorials: multimodal AI, function calling, grounding.",
            "video_count": 36,
            "view_count": 270000,
        },
        {
            "name": "[SYNTHETIC] RAG Masterclass",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@RAGMasterclass_FAKE",
            "channel_id": "FAKE_UCGs8vW2z5Aq7tU9jB6lLTt",
            "followers": 19200,
            "description": "SYNTHETIC TEST RECORD. Retrieval-Augmented Generation masterclass: chunking, embeddings, re-ranking, evaluation. 📧 ragmaster@aiclass.io",
            "video_count": 72,
            "view_count": 780000,
        },
        {
            "name": "[SYNTHETIC] Agentic AI Dev",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@AgenticAIDev_FAKE",
            "channel_id": "FAKE_UCHt9wX3a6Br8uV0kC7mMUu",
            "followers": 37500,
            "description": "SYNTHETIC TEST RECORD. Building AI agents with LangGraph, OpenAI tools, and function calling. The future of AI development.",
            "video_count": 103,
            "view_count": 1950000,
        },

        # ── GROUP 3: >100K subs — REJECTED (above micro range) ───────────────
        {
            "name": "[SYNTHETIC] DeepMind Digest",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@DeepMindDigest_FAKE",
            "channel_id": "FAKE_UCIu0xY4b7Cs9vW1lD8nNVv",
            "followers": 125000,
            "description": "SYNTHETIC TEST RECORD. AI research news and paper breakdowns. From DeepMind, OpenAI, Anthropic.",
            "video_count": 234,
            "view_count": 8900000,
        },
        {
            "name": "[SYNTHETIC] Python Universe",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@PythonUniverse_FAKE",
            "channel_id": "FAKE_UCJv1yZ5c8Dt0wX2mE9oOWw",
            "followers": 287000,
            "description": "SYNTHETIC TEST RECORD. Everything Python: web, automation, data science, and machine learning.",
            "video_count": 412,
            "view_count": 24000000,
        },
        {
            "name": "[SYNTHETIC] AI Mastery Academy",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@AIMasteryAcademy_FAKE",
            "channel_id": "FAKE_UCKw2zA6d9Eu1xY3nF0pPXx",
            "followers": 431000,
            "description": "SYNTHETIC TEST RECORD. Complete AI courses: machine learning, deep learning, NLP. Free certification.",
            "video_count": 567,
            "view_count": 41000000,
        },
        {
            "name": "[SYNTHETIC] Code With AI",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@CodeWithAI_FAKE",
            "channel_id": "FAKE_UCLx3aB1e5Fv7zA4oG1qQYy",
            "followers": 198000,
            "description": "SYNTHETIC TEST RECORD. AI-assisted coding: GitHub Copilot, Cursor, and building apps 10x faster.",
            "video_count": 298,
            "view_count": 14000000,
        },
        {
            "name": "[SYNTHETIC] Data Science Daily",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@DataScienceDaily_FAKE",
            "channel_id": "FAKE_UCMy4bC2f6Gw8aB5pH2rKRr",
            "followers": 345000,
            "description": "SYNTHETIC TEST RECORD. Data science every day: stats, visualisation, ML, and real-world projects.",
            "video_count": 489,
            "view_count": 31000000,
        },
        {
            "name": "[SYNTHETIC] ML Explained",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@MLExplained_FAKE",
            "channel_id": "FAKE_UCNz9cD3g7Hx9aB1qI8rKsAs",
            "followers": 512000,
            "description": "SYNTHETIC TEST RECORD. Machine learning explained visually. Math-first approach to understanding algorithms.",
            "video_count": 623,
            "view_count": 52000000,
        },
        {
            "name": "[SYNTHETIC] AI Today",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@AIToday_FAKE",
            "channel_id": "FAKE_UCOa0dE5h8Iz0cD3sK0tUCt",
            "followers": 267000,
            "description": "SYNTHETIC TEST RECORD. The latest in AI news, tools, and breakthroughs. Daily updates.",
            "video_count": 867,
            "view_count": 28000000,
        },
        {
            "name": "[SYNTHETIC] TensorFlow Hub",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@TensorFlowHub_FAKE",
            "channel_id": "FAKE_UCPb1eF6i9Jz1cD3sL0tVCu",
            "followers": 189000,
            "description": "SYNTHETIC TEST RECORD. TensorFlow tutorials from beginner to expert. Keras, TFX, TensorFlow Lite.",
            "video_count": 334,
            "view_count": 17000000,
        },
        {
            "name": "[SYNTHETIC] AI Entrepreneur",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@AIEntrepreneur_FAKE",
            "channel_id": "FAKE_UCQc2fG7j0La2dE4uM2vXEv",
            "followers": 423000,
            "description": "SYNTHETIC TEST RECORD. Building AI companies: SaaS, products, and AI consulting businesses.",
            "video_count": 498,
            "view_count": 38000000,
        },
        {
            "name": "[SYNTHETIC] Neural Networks 101",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@NeuralNetworks101_FAKE",
            "channel_id": "FAKE_UCRd3gH8k1Lb3eF5uN3wXFw",
            "followers": 156000,
            "description": "SYNTHETIC TEST RECORD. Neural networks from scratch in NumPy, then PyTorch. Theory meets practice.",
            "video_count": 245,
            "view_count": 11000000,
        },
        {
            "name": "[SYNTHETIC] The AI Lab",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@TheAILab_FAKE",
            "channel_id": "FAKE_UCSe4hI9l2Mc4fG6vO4xYGx",
            "followers": 376000,
            "description": "SYNTHETIC TEST RECORD. Experiments in AI: from GPT-4 jailbreaks to robotic process automation.",
            "video_count": 532,
            "view_count": 34000000,
        },
        {
            "name": "[SYNTHETIC] Full Stack AI",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@FullStackAI_FAKE",
            "channel_id": "FAKE_UCTf5jJ0n4Of6iJ8yR5zAJy",
            "followers": 231000,
            "description": "SYNTHETIC TEST RECORD. Full-stack AI development: React frontends, FastAPI backends, LLM integrations.",
            "video_count": 321,
            "view_count": 19000000,
        },
        {
            "name": "[SYNTHETIC] AI Code Review",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@AICodeReview_FAKE",
            "channel_id": "FAKE_UCUg7kL1o5Pf7jK9zS6bBKz",
            "followers": 167000,
            "description": "SYNTHETIC TEST RECORD. Live AI code reviews and pair programming sessions with AI assistants.",
            "video_count": 278,
            "view_count": 13000000,
        },
        {
            "name": "[SYNTHETIC] Robotics & AI",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@RoboticsAndAI_FAKE",
            "channel_id": "FAKE_UCVh8lM3p6Qg8kL0aT7cCLa",
            "followers": 298000,
            "description": "SYNTHETIC TEST RECORD. Where robotics meets AI: ROS2, autonomous driving, drone AI, and embodied intelligence.",
            "video_count": 389,
            "view_count": 25000000,
        },
        {
            "name": "[SYNTHETIC] Generative AI Hub",
            "platform": "YouTube",
            "profile_url": "https://youtube.com/@GenerativeAIHub_FAKE",
            "channel_id": "FAKE_UCWi9mN4q7Rh9mM2cU8eELb",
            "followers": 445000,
            "description": "SYNTHETIC TEST RECORD. The definitive generative AI channel: image, audio, video generation and multimodal AI.",
            "video_count": 612,
            "view_count": 44000000,
        },
    ]
