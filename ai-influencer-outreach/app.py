import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

# Discovery
from src.discovery import discover_influencers, save_raw_data

# Filtering  
from src.filtering import filter_influencers

# Enrichment
from src.enrichment import enrich_all

# Personalization
from src.personalization import personalize_all

# Email Sending
from src.email_sender import send_all_outreach

# Tracker
from src.tracker import create_outreach_log, get_outreach_summary_from_df

# Database
from src.database import init_db, insert_influencers_bulk, insert_outreach, clear_database
from src.sample_data import real_data_available

st.set_page_config(
    page_title="AI Influencer Outreach System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        background-attachment: fixed;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
    }

    /* Metric Cards */
    .metric-card-green { border-left: 5px solid #00E676; }
    .metric-card-blue { border-left: 5px solid #2979FF; }
    .metric-card-orange { border-left: 5px solid #FF9100; }
    .metric-card-red { border-left: 5px solid #FF1744; }

    /* Gradient Text */
    .gradient-text {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        margin-bottom: 10px;
    }

    /* Status Badges */
    .badge-passed, .badge-simulated, .badge-sent {
        background: rgba(0, 230, 118, 0.2);
        color: #00E676;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: 600;
    }
    .badge-rejected, .badge-failed {
        background: rgba(255, 23, 68, 0.2);
        color: #FF1744;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: 600;
    }
    .badge-review {
        background: rgba(255, 145, 0, 0.2);
        color: #FF9100;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: 600;
    }
    .badge-not-ready {
        background: rgba(41, 121, 255, 0.2);
        color: #2979FF;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: 600;
    }

    /* Button Styling */
    div.stButton > button {
        background: linear-gradient(90deg, #4776E6 0%, #8E54E9 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: opacity 0.3s;
        width: 100%;
    }
    div.stButton > button:hover {
        opacity: 0.9;
        color: white;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        border-bottom: 3px solid #00C9FF;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'df_raw' not in st.session_state:
    st.session_state.df_raw = None
if 'df_filtered' not in st.session_state:
    st.session_state.df_filtered = None
if 'df_enriched' not in st.session_state:
    st.session_state.df_enriched = None
if 'df_personalized' not in st.session_state:
    st.session_state.df_personalized = None
if 'outreach_results' not in st.session_state:
    st.session_state.outreach_results = []
if 'pipeline_stage' not in st.session_state:
    st.session_state.pipeline_stage = 'idle'
if 'db_initialized' not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h2 class='gradient-text'>🚀 AI Influencer Outreach</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#ccc; font-size:0.9em;'>Automated Micro-Influencer Discovery & Outreach Pipeline</p>", unsafe_allow_html=True)
    st.divider()

    st.markdown("### 🔑 API Configuration")
    yt_api_key = st.text_input("YouTube API Key", type="password", value=os.getenv("YOUTUBE_API_KEY", ""),
                               help="Free key for fetching real YouTube data. Required by assignment.")
    gemini_api_key = st.text_input("Gemini API Key (optional)", type="password", value=os.getenv("GEMINI_API_KEY", ""),
                                   help="Google Gemini 1.5 Flash — free at aistudio.google.com")
    hf_api_key = st.text_input("HuggingFace API Key (optional)", type="password", value=os.getenv("HUGGINGFACE_API_KEY", ""),
                               help="Free alternative to Gemini — Mistral-7B via HF Inference API. Get key at huggingface.co/settings/tokens")
    # ── AI backend status ─────────────────────────────────────────
    if gemini_api_key:
        st.success("✅ AI: Google Gemini 1.5 Flash")
    elif hf_api_key:
        st.success("✅ AI: HuggingFace Mistral-7B")
    else:
        st.info("ℹ️ AI: Template fallback (add Gemini or HuggingFace key for AI messages)")

    if real_data_available():
        st.success("✅ Real YouTube data available (data/raw_influencers.csv)")
    elif yt_api_key:
        st.info("🔍 YouTube API key set — Discovery will fetch REAL data")
    else:
        st.warning(
            "⚠️ No real data yet.\n\n"
            "**The assignment requires real data.**\n\n"
            "**Option 1 (Recommended):** Add your YouTube API key above, "
            "then click ‘Run Discovery’.\n\n"
            "**Option 2:** Run in terminal:\n"
            "```\npython fetch_real_data.py --api-key YOUR_KEY\n```\n\n"
            "Get a FREE key → [console.cloud.google.com](https://console.cloud.google.com/)"
        )
    st.divider()

    st.markdown("### ⚙️ Pipeline Controls")
    
    if st.button("🔍 Run Discovery"):
        with st.spinner("Discovering influencers..."):
            try:
                df = discover_influencers(api_key=yt_api_key if yt_api_key else None)
                if not df.empty:
                    save_raw_data(df)
                    st.session_state.df_raw = df
                    st.session_state.pipeline_stage = 'discovered'
                    # Check if data is real or synthetic
                    is_real = real_data_available() or bool(yt_api_key)
                    has_synthetic = df['name'].astype(str).str.startswith('[SYNTHETIC]').any() if 'name' in df.columns else False
                    if has_synthetic:
                        st.warning(
                            f"⚠️ Loaded {len(df)} SYNTHETIC records (demo only). "
                            "Add a YouTube API key for REAL data required by the assignment."
                        )
                    else:
                        st.success(f"✅ Found {len(df)} real YouTube channels!")
                else:
                    st.warning("No influencers found.")
            except Exception as e:
                st.error(f"Discovery Error: {str(e)}")
    if st.button("🎯 Filter & Score"):
        if st.session_state.df_raw is not None:
            with st.spinner("Filtering and scoring..."):
                try:
                    df = filter_influencers(st.session_state.df_raw.copy())
                    st.session_state.df_filtered = df
                    st.session_state.pipeline_stage = 'filtered'
                    st.success("Filtering complete!")
                except Exception as e:
                    st.error(f"Filter Error: {str(e)}")
        else:
            st.warning("Run Discovery first!")

    if st.button("📊 Enrich Profiles"):
        if st.session_state.df_filtered is not None:
            with st.spinner("Enriching profiles..."):
                try:
                    df = enrich_all(st.session_state.df_filtered.copy())
                    st.session_state.df_enriched = df
                    st.session_state.pipeline_stage = 'enriched'
                    st.success("Enrichment complete!")
                except Exception as e:
                    st.error(f"Enrichment Error: {str(e)}")
        else:
            st.warning("Run Filtering first!")

    if st.button("🤖 Generate AI Messages"):
        if st.session_state.df_enriched is not None:
            gemini_key = gemini_api_key if gemini_api_key else None
            hf_key = hf_api_key if hf_api_key else None
            if gemini_key:
                mode_msg = "Using Gemini AI..."
            elif hf_key:
                mode_msg = "Using HuggingFace Mistral-7B..."
            else:
                mode_msg = "Using template fallback (no API key)..."
            with st.spinner(f"Generating personalized messages... {mode_msg}"):
                try:
                    df = personalize_all(
                        st.session_state.df_enriched.copy(),
                        api_key=gemini_key,
                        hf_api_key=hf_key
                    )
                    st.session_state.df_personalized = df
                    st.session_state.pipeline_stage = 'personalized'
                    if gemini_key:
                        st.success("✅ Messages generated with Google Gemini!")
                    elif hf_key:
                        st.success("✅ Messages generated with HuggingFace Mistral-7B!")
                    else:
                        st.success("✅ Messages generated with templates! (Add an AI key for richer messages)")
                except Exception as e:
                    st.error(f"Personalization Error: {str(e)}")
        else:
            st.warning("Run Enrichment first!")

    if st.button("📨 Run Dry-Run Sending"):
        if st.session_state.df_personalized is not None:
            with st.spinner("Simulating outreach..."):
                try:
                    results = send_all_outreach(st.session_state.df_personalized.copy(), dry_run=True)
                    st.session_state.outreach_results = results
                    st.session_state.pipeline_stage = 'sent'
                    st.success("Dry-run complete!")
                except Exception as e:
                    st.error(f"Sending Error: {str(e)}")
        else:
            st.warning("Run AI Messages generation first!")

    if st.button("💾 Save to Database"):
        if st.session_state.pipeline_stage != 'idle':
            with st.spinner("Saving to database..."):
                try:
                    df_to_save = st.session_state.df_personalized if st.session_state.df_personalized is not None else (
                                 st.session_state.df_enriched if st.session_state.df_enriched is not None else (
                                 st.session_state.df_filtered if st.session_state.df_filtered is not None else st.session_state.df_raw))
                    # Convert DataFrame to list of dicts for database insertion
                    records = df_to_save.to_dict('records') if hasattr(df_to_save, 'to_dict') else df_to_save
                    insert_influencers_bulk(records)
                    if st.session_state.outreach_results:
                        for result in st.session_state.outreach_results:
                            outreach_record = {
                                'influencer_id': 0,
                                'email': result.get('email', ''),
                                'email_message': '',
                                'instagram_dm': '',
                                'sent_date': result.get('sent_date', ''),
                                'status': result.get('status', 'NOT_READY'),
                                'error_message': result.get('error_message', '')
                            }
                            insert_outreach(outreach_record)
                    st.success("Saved to database successfully!")
                except Exception as e:
                    st.error(f"Database Error: {str(e)}")
        else:
            st.warning("Nothing to save. Run pipeline first.")

    st.divider()
    
    if st.session_state.df_filtered is not None:
        st.markdown("### 📈 Quick Stats")
        df = st.session_state.df_filtered
        total = len(df)
        passed = len(df[df['filter_status'] == 'Passed']) if 'filter_status' in df.columns else 0
        rejected = total - passed
        st.write(f"Total: {total}")
        st.write(f"Qualified: {passed}")
        st.write(f"Rejected: {rejected}")
        
    if st.button("🔄 Reset Pipeline"):
        st.session_state.df_raw = None
        st.session_state.df_filtered = None
        st.session_state.df_enriched = None
        st.session_state.df_personalized = None
        st.session_state.outreach_results = []
        st.session_state.pipeline_stage = 'idle'
        st.rerun()

# --- Main Area ---
st.markdown("<h1 class='gradient-text'>AI Influencer Outreach Dashboard</h1>", unsafe_allow_html=True)

tabs = st.tabs(["📊 Dashboard", "👥 All Influencers", "✅ Qualified Influencers", "✉️ AI Messages", "📬 Outreach Tracker"])

# Helper function to get current latest dataframe
def get_current_df():
    if st.session_state.df_personalized is not None: return st.session_state.df_personalized
    if st.session_state.df_enriched is not None: return st.session_state.df_enriched
    if st.session_state.df_filtered is not None: return st.session_state.df_filtered
    return st.session_state.df_raw

df = get_current_df()

# --- Tab 1: Dashboard ---
with tabs[0]:
    if df is not None:
        # Metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_discovered = len(df)
        qualified = len(df[df['filter_status'] == 'Passed']) if 'filter_status' in df.columns else 0
        rejected = len(df[df['filter_status'] == 'Rejected']) if 'filter_status' in df.columns else 0
        emails_found = len(df[(df['email'].notna()) & (df['email'] != '') & (df['email'] != 'Not Found')]) if 'email' in df.columns else 0
        outreach_sent = len([r for r in st.session_state.outreach_results if r['status'] in ('SENT', 'SIMULATED')]) if st.session_state.outreach_results else 0

        with col1:
            st.markdown(f"<div class='glass-card metric-card-blue'><h4>Total Discovered</h4><h2>{total_discovered}</h2></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='glass-card metric-card-green'><h4>Qualified</h4><h2>{qualified}</h2></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='glass-card metric-card-red'><h4>Rejected</h4><h2>{rejected}</h2></div>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<div class='glass-card metric-card-orange'><h4>Emails Found</h4><h2>{emails_found}</h2></div>", unsafe_allow_html=True)
        with col5:
            st.markdown(f"<div class='glass-card metric-card-blue'><h4>Outreach Sent</h4><h2>{outreach_sent}</h2></div>", unsafe_allow_html=True)

        # Charts
        if 'filter_status' in df.columns:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.subheader("Filter Status")
                status_counts = df['filter_status'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']
                fig_pie = px.pie(status_counts, names='Status', values='Count', hole=0.4,
                                 color='Status', color_discrete_map={'Passed':'#00E676', 'Rejected':'#FF1744'},
                                 template="plotly_dark")
                fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_pie, use_container_width=True)

            with col_chart2:
                if 'classification' in df.columns:
                    st.subheader("Score Classification")
                    class_counts = df['classification'].value_counts().reset_index()
                    class_counts.columns = ['Classification', 'Count']
                    fig_bar = px.bar(class_counts, x='Classification', y='Count',
                                     color='Classification', 
                                     color_discrete_map={'Excellent':'#00E676', 'Good':'#2979FF', 'Review':'#FF9100', 'Reject':'#FF1744'},
                                     template="plotly_dark")
                    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            if 'score' in df.columns:
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.subheader("Score Distribution")
                fig_hist = px.histogram(df, x='score', nbins=20, template="plotly_dark", color_discrete_sequence=['#00C9FF'])
                fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_hist, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.info("Run the pipeline from the sidebar to get started! 🚀")

# --- Tab 2: All Influencers ---
with tabs[1]:
    if df is not None:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        col_search, col_filter, col_sort = st.columns([2, 1, 1])
        with col_search:
            search_term = st.text_input("🔍 Search Influencers", "")
        with col_filter:
            filter_opt = st.selectbox("Filter Status", ["All", "Passed", "Rejected"]) if 'filter_status' in df.columns else st.selectbox("Filter Status", ["All"])
        with col_sort:
            sort_opt = st.selectbox("Sort By", ["None", "Followers", "Name", "Score"] if 'score' in df.columns else ["None", "Followers", "Name"])

        # Apply filters
        display_df = df.copy()
        if search_term:
            display_df = display_df[display_df['name'].str.contains(search_term, case=False, na=False)]
        
        if filter_opt != "All" and 'filter_status' in display_df.columns:
            display_df = display_df[display_df['filter_status'] == filter_opt]
            
        if sort_opt == "Followers" and 'followers' in display_df.columns:
            display_df = display_df.sort_values(by='followers', ascending=False)
        elif sort_opt == "Name" and 'name' in display_df.columns:
            display_df = display_df.sort_values(by='name', ascending=True)
        elif sort_opt == "Score" and 'score' in display_df.columns:
            display_df = display_df.sort_values(by='score', ascending=False)

        st.write(f"Showing {len(display_df)} influencers")
        
        cols_to_show = ['name', 'platform', 'followers']
        if 'filter_status' in display_df.columns: cols_to_show.extend(['filter_status', 'filter_reason', 'score', 'classification'])
        
        st.dataframe(display_df[cols_to_show], use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No data available.")

# --- Tab 3: Qualified Influencers ---
with tabs[2]:
    if df is not None and 'filter_status' in df.columns:
        qualified_df = df[df['filter_status'] == 'Passed']
        if not qualified_df.empty:
            for _, row in qualified_df.iterrows():
                name = row.get('name', 'Unknown')
                score = row.get('score', 0)
                classification = row.get('classification', 'N/A')
                
                with st.expander(f"🟢 {name} — Score: {score}/100 ({classification})"):
                    st.markdown("<div class='glass-card' style='margin-bottom:0;'>", unsafe_allow_html=True)
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.write(f"**Platform:** {row.get('platform', 'N/A')}")
                        st.write(f"**Followers:** {row.get('followers', 'N/A'):,}")
                        st.write(f"**Engagement Rate:** {row.get('engagement_rate', 'N/A')}")
                        st.write(f"**Profile URL:** [{name}]({row.get('profile_url', '#')})")
                    with col_info2:
                        st.write(f"**Niche:** {row.get('niche', 'N/A')}")
                        st.write(f"**Content Themes:** {row.get('content_themes', 'N/A')}")
                        st.write(f"**Email:** {row.get('email', 'N/A')}")
                        st.write(f"**Website:** {row.get('website', 'N/A')}")
                    
                    st.progress(int(score) if pd.notnull(score) else 0, text=f"Score: {score}")
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No qualified influencers found.")
    else:
        st.info("Run Filtering to see qualified influencers.")

# --- Tab 4: AI Messages ---
with tabs[3]:
    if st.session_state.df_personalized is not None:
        df_p = st.session_state.df_personalized
        msg_df = df_p.dropna(subset=['email_pitch', 'instagram_dm'], how='all')
        if not msg_df.empty:
            for _, row in msg_df.iterrows():
                name = row.get('name', 'Unknown')
                with st.expander(f"✉️ {name}"):
                    st.markdown("<div class='glass-card' style='margin-bottom:0;'>", unsafe_allow_html=True)
                    
                    if pd.notnull(row.get('content_analysis')):
                        st.write("**Content Analysis:**")
                        st.info(row['content_analysis'])
                    
                    col_email, col_dm = st.columns(2)
                    with col_email:
                        st.write("📧 **Email Pitch**")
                        email_txt = row.get('email_pitch', 'N/A')
                        st.code(email_txt, language="markdown")
                        word_count = len(str(email_txt).split())
                        st.caption(f"{word_count} words")
                        
                    with col_dm:
                        st.write("💬 **Instagram DM**")
                        dm_txt = row.get('instagram_dm', 'N/A')
                        st.code(dm_txt, language="markdown")
                        word_count = len(str(dm_txt).split())
                        st.caption(f"{word_count} words")
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No generated messages available.")
    else:
        st.info("Run 'Generate AI Messages' to see this tab.")

# --- Tab 5: Outreach Tracker ---
with tabs[4]:
    if st.session_state.outreach_results and df is not None:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        try:
            summary = get_outreach_summary_from_df(df, st.session_state.outreach_results)
            col_s1, col_s2, col_s3, col_s4, col_s5, col_s6 = st.columns(6)
            col_s1.metric("Total", summary.get('total_discovered', 0))
            col_s2.metric("Simulated", summary.get('emails_simulated', 0))
            col_s3.metric("Sent", summary.get('emails_sent', 0))
            col_s4.metric("Failed", summary.get('emails_failed', 0))
            col_s5.metric("Skipped", summary.get('skipped_duplicate', 0))
            col_s6.metric("No Email", summary.get('no_email', 0))
        except Exception as e:
            st.error(f"Could not load summary: {str(e)}")

        st.subheader("Outreach Log")
        try:
            log_df = create_outreach_log(df, st.session_state.outreach_results)
            
            def color_status(val):
                if val in ('SENT', 'SIMULATED'): return 'color: #00E676; font-weight:bold;'
                if val == 'FAILED': return 'color: #FF1744; font-weight:bold;'
                return 'color: #2979FF;'
            
            st.dataframe(log_df.style.applymap(color_status, subset=['status']), use_container_width=True, hide_index=True)
            
            csv = log_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Outreach Log as CSV", csv, "outreach_log.csv", "text/csv")
        except Exception as e:
            st.error(f"Could not load log: {str(e)}")
            
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Run Dry-Run Sending to generate the outreach log.")
