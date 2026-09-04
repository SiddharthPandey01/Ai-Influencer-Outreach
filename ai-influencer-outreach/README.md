# 🚀 AI-Powered Micro-Influencer Outreach System

An automated pipeline that discovers, filters, enriches, and contacts micro-influencers in the **Technology / AI / Generative AI** niche using YouTube as the primary data source and Google Gemini for AI-powered personalization.

---

## 📋 Problem Statement

Brands and startups struggle to identify and reach out to relevant micro-influencers (5K–100K followers) efficiently. Manual discovery, filtering, and outreach is time-consuming, error-prone, and doesn't scale. This system automates the entire pipeline — from discovery to personalized outreach — while maintaining quality and compliance.

---

## ✨ Features

- **Automated Discovery** — Searches YouTube for AI/tech creators using multiple search terms via the YouTube Data API v3, with sample data fallback
- **Data Cleaning** — Removes duplicates, normalizes data, validates URLs and follower counts
- **Smart Filtering** — Applies micro-influencer criteria (5K–100K followers) with niche relevance checking
- **100-Point Scoring** — Evaluates influencers across 5 dimensions: follower fit, engagement, niche relevance, content relevance, profile completeness
- **Profile Enrichment** — Extracts business emails, calculates YouTube engagement rate, determines niche and content themes
- **AI Content Analysis** — Uses Google Gemini to analyze creator content and identify collaboration angles
- **Personalized Emails** — Generates unique 60–90 word collaboration emails per influencer
- **Personalized Instagram DMs** — Generates unique 15–30 word DMs per influencer
- **Dry-Run Sending** — Simulates email delivery before any real outreach
- **Duplicate Prevention** — Checks outreach history to prevent contacting the same influencer twice
- **SQLite Database** — Stores influencer profiles and outreach records
- **Streamlit Dashboard** — Premium dark-themed UI with 5 interactive tabs

---

## 🏗️ Architecture / Workflow

```
Discovery → Cleaning → Filtering → Enrichment → AI Personalization → Sending → Tracking
```

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  YouTube API │ →  │  Raw CSV     │ →  │  Clean &     │
│  / Sample    │    │  (50+ recs)  │    │  Filter      │
└──────────────┘    └──────────────┘    └──────────────┘
                                              │
                    ┌──────────────┐    ┌──────┴───────┐
                    │  Gemini AI   │ ←  │  Enrich      │
                    │  Analysis    │    │  Profiles    │
                    └──────┬───────┘    └──────────────┘
                           │
                    ┌──────┴───────┐    ┌──────────────┐
                    │  Generate    │ →  │  Dry-Run     │
                    │  Email + DM  │    │  Sending     │
                    └──────────────┘    └──────┬───────┘
                                              │
                    ┌──────────────┐    ┌──────┴───────┐
                    │  Streamlit   │ ←  │  SQLite      │
                    │  Dashboard   │    │  Tracking    │
                    └──────────────┘    └──────────────┘
```

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.10+ |
| Data Processing | Pandas |
| Discovery API | YouTube Data API v3 |
| AI / LLM | Google Gemini 1.5 Flash (free tier) |
| Database | SQLite |
| Email | SMTP (Gmail) / Dry-run simulation |
| Dashboard | Streamlit |
| Charts | Plotly |
| Config | python-dotenv |
| Version Control | Git / GitHub |

---

## 🔌 APIs & Tools Used

| API / Tool | Purpose | Cost |
|---|---|---|
| YouTube Data API v3 | Influencer discovery | Free (10,000 units/day) |
| Google Gemini 1.5 Flash | Content analysis & message generation | Free (60 req/min) |
| Gmail SMTP | Email sending (dry-run by default) | Free |
| Streamlit | Web dashboard | Free |

---

## 📊 Data Sources

- **Primary**: YouTube Data API v3 — searches for channels matching AI/tech keywords
- **Fallback**: Pre-seeded sample data (55 influencers) for demo without API keys
- **Search Terms**: `AI tools`, `Generative AI`, `Machine Learning`, `Python tutorial`, `LLM tutorial`, `RAG tutorial`, `LangChain`, `deep learning`, `artificial intelligence`, `data science Python`

---

## 🔍 Discovery Methodology

1. Search YouTube for channels matching AI/tech search terms
2. Retrieve channel statistics (subscribers, videos, views) and descriptions
3. Deduplicate by channel ID
4. Save raw results to `data/raw_influencers.csv`
5. Target: 50–100 creators per run

---

## 🎯 Filtering Logic

### Micro-Influencer Criteria
- **Minimum followers**: 5,000
- **Maximum followers**: 100,000
- **Niche relevance**: Must contain tech/AI keywords in description

### 100-Point Scoring System

| Category | Max Points | Logic |
|---|---|---|
| Follower Fit | 20 | Optimal 10K–50K = 20, edges = 15, outside = 0 |
| Engagement | 25 | Views-to-subscriber ratio scoring |
| Niche Relevance | 25 | Tech keyword density in description |
| Content Relevance | 20 | AI-specific term bonus (LLM, GPT, RAG, etc.) |
| Profile Completeness | 10 | Has bio (+3), email (+4), videos (+3) |

### Classification
| Score | Classification |
|---|---|
| 80–100 | Excellent |
| 60–79 | Good |
| 40–59 | Review |
| < 40 | Reject |

Every influencer receives a `filter_status` (Passed/Rejected) and `filter_reason` explaining the decision.

---

## 📈 Enrichment Process

For each influencer, the system collects:

| Field | Status | Source |
|---|---|---|
| Name | Mandatory | YouTube API / Sample |
| Platform | Mandatory | Set to "YouTube" |
| Profile URL | Mandatory | YouTube API / Sample |
| Follower Count | Mandatory | YouTube API / Sample |
| Engagement Rate | Mandatory | Calculated: `(Avg Views per Video / Subscribers) × 100` |
| Niche | Mandatory | Keyword analysis of description |
| Content Themes | Mandatory | Keyword extraction from description |
| Contact Email | Mandatory | Extracted from description via regex, or `Not Found` |
| Website | Optional | Extracted from description, or `Not Found` |

**Email Discovery**: Emails are ONLY extracted from public channel descriptions using regex. No email addresses are guessed or fabricated. If no email is found, the field is set to `Not Found`.

---

## 🤖 AI Model & Prompt Approach

**Model**: Google Gemini 1.5 Flash (free tier)

**Content Analysis Prompt**: Sends creator name, platform, subscribers, description, and recent video titles. Requests structured JSON output with niche, content themes, tone, audience, and collaboration angle.

**Fallback**: When Gemini API is unavailable, a template-based system derives analysis from description keywords (12+ niche categories, 20+ theme mappings).

---

## ✉️ Personalization Logic

### Email (60–90 words)
- Mentions creator name, specific niche, and content themes
- References their audience and content tone
- Proposes a concrete collaboration idea
- Each email is unique (hash-based template selection or Gemini generation)

### Instagram DM (15–30 words)
- Natural, conversational tone
- References specific content topic
- Brief collaboration mention
- Each DM is unique

**Template Variety**: 5 distinct email templates and 5 DM templates selected via name-hash for deterministic variety.

---

## 📨 Sending Mechanism

### Dry-Run Mode (Default)
```
[DRY RUN] Would send email to: creator@example.com
  Subject: Collaboration Opportunity — AI Tools x CreatorName
  Status: SIMULATED
```

### Pre-Send Checks
1. Does the influencer have a valid contact email?
2. Has this influencer already been contacted? (duplicate prevention)
3. Is the generated message available?
4. Is the system in dry-run or real-send mode?

### Real Mode
Uses Gmail SMTP with app password authentication. Only activated when `DRY_RUN=False` in `.env`.

---

## 🗄️ Database / Outreach Tracking

### SQLite Tables

**`influencers`**: id, name, platform, profile_url, followers, engagement_rate, niche, content_themes, email, filter_status, filter_reason, score, classification

**`outreach`**: id, influencer_id, email, email_message, instagram_dm, sent_date, status, error_message

### Outreach Statuses
| Status | Meaning |
|---|---|
| `NOT_READY` | Message not generated yet |
| `SIMULATED` | Dry-run successful |
| `SENT` | Email actually sent |
| `FAILED` | Sending error occurred |
| `SKIPPED_DUPLICATE` | Already contacted this email |
| `NO_EMAIL` | No valid email address found |

---

## ⚠️ Limitations

1. **Single Platform**: Currently only supports YouTube as discovery source
2. **Single Niche**: Focused on Technology / AI / Generative AI
3. **Email Discovery**: Limited to emails found in public channel descriptions
4. **Instagram DM**: Generated but not auto-sent (simulated/manual workflow)
5. **Engagement Rate**: Uses YouTube-specific formula; not comparable cross-platform
6. **No Real-time Data**: Subscriber counts are from time of API call
7. **API Quotas**: YouTube API has 10,000 units/day limit; Gemini has 60 req/min
8. **Template Fallback**: Without Gemini API key, messages use template-based generation (still personalized, but less varied)

---

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-influencer-outreach.git
cd ai-influencer-outreach
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

If activation is blocked on Windows:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
```bash
copy .env.example .env
```

Edit `.env` with your API keys:
```env
YOUTUBE_API_KEY=your_youtube_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_gmail_app_password_here
DRY_RUN=True
```

> **Note**: The system works without API keys using sample data and template-based messages.

### 5. Get Free API Keys
- **YouTube Data API**: [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- **Gemini API**: [Google AI Studio](https://aistudio.google.com/apikey)

---

## ▶️ How to Run

```bash
streamlit run app.py
```

Then use the sidebar buttons in order:
1. 🔍 **Run Discovery** — Discovers 55 influencers (sample data or YouTube API)
2. 🎯 **Filter & Score** — Applies micro-influencer criteria and 100-point scoring
3. 📊 **Enrich Profiles** — Extracts emails, calculates engagement, determines niche
4. 🤖 **Generate AI Messages** — Creates personalized emails and DMs
5. 📨 **Run Dry-Run Sending** — Simulates email delivery
6. 💾 **Save to Database** — Persists everything to SQLite

---

## 📸 Dashboard Tabs

| Tab | Description |
|---|---|
| 📊 Dashboard | KPI cards, pie chart, bar chart, score histogram |
| 👥 All Influencers | Searchable/sortable table with filter status |
| ✅ Qualified | Expandable profile cards with score breakdown |
| ✉️ AI Messages | Side-by-side email and DM with word counts |
| 📬 Outreach Tracker | Full log with status, export to CSV |

---

## 📁 Project Structure

```
ai-influencer-outreach/
├── app.py                      # Streamlit dashboard
├── requirements.txt            # Python dependencies
├── .env.example                # API key template
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
│
├── data/
│   ├── raw_influencers.csv     # Raw discovery output
│   ├── enriched_influencers.csv # Enriched + filtered data
│   └── outreach_log.csv        # Outreach status export
│
├── database/
│   └── outreach.db             # SQLite database (runtime)
│
├── src/
│   ├── __init__.py
│   ├── sample_data.py          # 55 pre-seeded sample influencers
│   ├── database.py             # SQLite CRUD operations
│   ├── discovery.py            # YouTube API discovery
│   ├── filtering.py            # Cleaning, filtering, scoring
│   ├── enrichment.py           # Profile enrichment
│   ├── personalization.py      # Gemini AI + template fallback
│   ├── email_sender.py         # SMTP / dry-run sending
│   └── tracker.py              # Outreach status tracking
│
└── prompts/
    └── outreach_prompt.txt     # LLM prompt templates
```

---

## 🙏 Acknowledgments

Built as part of the **EDXSO AI Engineer Intern Assignment 1**.
