import os
import pandas as pd
from datetime import datetime

def create_outreach_log(df, outreach_results):
    """
    Create a combined outreach log DataFrame.
    """
    results_df = pd.DataFrame(outreach_results)
    if results_df.empty:
        cols = ['name', 'platform', 'followers', 'niche', 'email', 'email_pitch', 'instagram_dm', 'sent_date', 'status', 'error_message']
        return pd.DataFrame(columns=cols)
        
    merged = pd.merge(df, results_df, on='email', how='left')
    
    if 'influencer_name' in merged.columns:
        merged['name'] = merged['name'].fillna(merged['influencer_name'])
        
    cols_to_keep = ['name', 'platform', 'followers', 'niche', 'email', 'email_pitch', 'instagram_dm', 'sent_date', 'status', 'error_message']
    
    for col in cols_to_keep:
        if col not in merged.columns:
            merged[col] = None
            
    return merged[cols_to_keep]

def export_log(log_df, path=None):
    """
    Export outreach log to CSV.
    """
    if path is None:
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'outreach_log.csv')
        
    os.makedirs(os.path.dirname(path), exist_ok=True)
    log_df.to_csv(path, index=False)

def get_outreach_summary(db_path=None):
    """
    Get summary statistics from the database.
    """
    try:
        from src.database import get_all_outreach, get_all_influencers
        
        influencers = get_all_influencers()
        outreach = get_all_outreach()
        
        total_discovered = len(influencers)
        qualified = len([i for i in influencers if i.get('filter_status') == 'Passed'])
        rejected = len([i for i in influencers if i.get('filter_status') == 'Rejected'])
        emails_found = len([i for i in influencers if i.get('email') and str(i.get('email')).lower() != 'not found'])
        
        emails_sent = len([o for o in outreach if o.get('status') == 'SENT'])
        emails_simulated = len([o for o in outreach if o.get('status') == 'SIMULATED'])
        emails_failed = len([o for o in outreach if o.get('status') == 'FAILED'])
        skipped_duplicate = len([o for o in outreach if o.get('status') == 'SKIPPED_DUPLICATE'])
        no_email = len([o for o in outreach if o.get('status') == 'NO_EMAIL'])
        not_ready = len([o for o in outreach if o.get('status') == 'NOT_READY'])
        
        return {
            'total_discovered': total_discovered,
            'qualified': qualified,
            'rejected': rejected,
            'emails_found': emails_found,
            'emails_sent': emails_sent,
            'emails_simulated': emails_simulated,
            'emails_failed': emails_failed,
            'skipped_duplicate': skipped_duplicate,
            'no_email': no_email,
            'not_ready': not_ready
        }
    except Exception as e:
        print(f"Could not load summary from database: {e}")
        return {}

def get_outreach_summary_from_df(df, outreach_results=None):
    """
    Compute summary from DataFrames instead of database.
    """
    total_discovered = len(df)
    qualified = len(df[df['filter_status'] == 'Passed'])
    rejected = len(df[df['filter_status'] == 'Rejected'])
    
    def has_email(email):
        return pd.notna(email) and str(email).strip().lower() not in ('', 'not found')
        
    emails_found = sum(df['email'].apply(has_email))
    
    summary = {
        'total_discovered': total_discovered,
        'qualified': qualified,
        'rejected': rejected,
        'emails_found': emails_found,
        'emails_sent': 0,
        'emails_simulated': 0,
        'emails_failed': 0,
        'skipped_duplicate': 0,
        'no_email': 0,
        'not_ready': 0
    }
    
    if outreach_results:
        for res in outreach_results:
            status = res.get('status', '').lower()
            if status == 'sent': summary['emails_sent'] += 1
            elif status == 'simulated': summary['emails_simulated'] += 1
            elif status == 'failed': summary['emails_failed'] += 1
            elif status == 'skipped_duplicate': summary['skipped_duplicate'] += 1
            elif status == 'no_email': summary['no_email'] += 1
            elif status == 'not_ready': summary['not_ready'] += 1
            
    return summary

def format_summary(summary):
    """
    Return a formatted string summary for display.
    """
    lines = [
        "📊 Outreach Summary",
        "━━━━━━━━━━━━━━━━━━━",
        f"Total Discovered: {summary.get('total_discovered', 0)}",
        f"Qualified: {summary.get('qualified', 0)}",
        f"Rejected: {summary.get('rejected', 0)}",
        f"Emails Found: {summary.get('emails_found', 0)}",
        "",
        "Outreach Status",
        "───────────────",
        f"Sent: {summary.get('emails_sent', 0)}",
        f"Simulated: {summary.get('emails_simulated', 0)}",
        f"Failed: {summary.get('emails_failed', 0)}",
        f"Skipped (Duplicate): {summary.get('skipped_duplicate', 0)}",
        f"No Email: {summary.get('no_email', 0)}",
        f"Not Ready: {summary.get('not_ready', 0)}"
    ]
    return "\n".join(lines)
