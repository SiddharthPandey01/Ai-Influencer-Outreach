import os
import sys
import sqlite3
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "outreach.db")

def init_db(db_path=None):
    """Create the database and tables if they don't exist."""
    path = db_path or DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS influencers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                platform TEXT,
                profile_url TEXT UNIQUE,
                followers INTEGER,
                engagement_rate REAL,
                niche TEXT,
                content_themes TEXT,
                email TEXT,
                filter_status TEXT,
                filter_reason TEXT,
                score INTEGER,
                classification TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outreach (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                influencer_id INTEGER,
                email TEXT,
                email_message TEXT,
                instagram_dm TEXT,
                sent_date TEXT,
                status TEXT DEFAULT 'NOT_READY',
                error_message TEXT,
                FOREIGN KEY (influencer_id) REFERENCES influencers(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"Database initialized at {path}")
    except Exception as e:
        print(f"Error initializing DB: {e}")

def insert_influencer(influencer, db_path=None):
    """Insert a single influencer dict. Use INSERT OR REPLACE to handle duplicates by profile_url."""
    path = db_path or DB_PATH
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        content_themes = influencer.get('content_themes', '')
        if isinstance(content_themes, list):
            content_themes = ','.join(content_themes)
            
        cursor.execute('''
            INSERT OR REPLACE INTO influencers (
                name, platform, profile_url, followers, engagement_rate, 
                niche, content_themes, email, filter_status, filter_reason, 
                score, classification
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            influencer.get('name'),
            influencer.get('platform'),
            influencer.get('profile_url'),
            influencer.get('followers'),
            influencer.get('engagement_rate'),
            influencer.get('niche'),
            content_themes,
            influencer.get('email'),
            influencer.get('filter_status'),
            influencer.get('filter_reason'),
            influencer.get('score'),
            influencer.get('classification')
        ))
        
        row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return row_id
    except Exception as e:
        print(f"Error inserting influencer: {e}")
        return None

def insert_influencers_bulk(influencers, db_path=None):
    """Insert multiple influencers. Clear existing data first."""
    path = db_path or DB_PATH
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM influencers')
        conn.commit()
        conn.close()
        for inf in influencers:
            insert_influencer(inf, path)
        print(f"Bulk inserted {len(influencers)} influencers.")
    except Exception as e:
        print(f"Error in bulk insert: {e}")

def insert_outreach(outreach, db_path=None):
    """Insert outreach record."""
    path = db_path or DB_PATH
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO outreach (
                influencer_id, email, email_message, instagram_dm, 
                sent_date, status, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            outreach.get('influencer_id'),
            outreach.get('email'),
            outreach.get('email_message'),
            outreach.get('instagram_dm'),
            outreach.get('sent_date'),
            outreach.get('status', 'NOT_READY'),
            outreach.get('error_message')
        ))
        row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return row_id
    except Exception as e:
        print(f"Error inserting outreach: {e}")
        return None

def get_all_influencers(db_path=None):
    """Return all influencers as list of dicts."""
    path = db_path or DB_PATH
    try:
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM influencers')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting influencers: {e}")
        return []

def get_qualified_influencers(db_path=None):
    """Return influencers where filter_status = 'Passed'."""
    path = db_path or DB_PATH
    try:
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM influencers WHERE filter_status = 'Passed'")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting qualified influencers: {e}")
        return []

def get_all_outreach(db_path=None):
    """Return all outreach records as list of dicts."""
    path = db_path or DB_PATH
    try:
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM outreach')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting outreach: {e}")
        return []

def is_already_contacted(email, db_path=None):
    """Check if email exists in outreach table with status SENT or SIMULATED."""
    path = db_path or DB_PATH
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM outreach WHERE email = ? AND status IN ('SENT', 'SIMULATED')", (email,))
        row = cursor.fetchone()
        conn.close()
        return row is not None
    except Exception as e:
        print(f"Error checking if contacted: {e}")
        return False

def get_outreach_summary(db_path=None):
    """Return dict with counts: total, simulated, sent, failed, skipped, no_email, not_ready"""
    path = db_path or DB_PATH
    summary = {
        'total': 0, 'simulated': 0, 'sent': 0, 'failed': 0, 
        'skipped': 0, 'no_email': 0, 'not_ready': 0
    }
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM outreach GROUP BY status")
        rows = cursor.fetchall()
        for status, count in rows:
            summary['total'] += count
            if status.lower() in summary:
                summary[status.lower()] = count
        conn.close()
        return summary
    except Exception as e:
        print(f"Error getting summary: {e}")
        return summary

def clear_database(db_path=None):
    """Delete all records from both tables."""
    path = db_path or DB_PATH
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM outreach')
        cursor.execute('DELETE FROM influencers')
        conn.commit()
        conn.close()
        print("Database cleared.")
    except Exception as e:
        print(f"Error clearing db: {e}")
