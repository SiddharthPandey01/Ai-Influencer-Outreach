"""
Email sending module for the AI Influencer Outreach System.
Supports DRY_RUN mode (default) and real SMTP sending via Gmail.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv


def send_email(to_email, subject, body, dry_run=True, sender_email=None, sender_password=None):
    """
    Send a single email.

    Pre-send checks:
    1. to_email must not be 'Not Found' or empty
    2. body must not be empty

    Returns: (status, error_message)
    Status values: SIMULATED, SENT, FAILED, NO_EMAIL
    """
    if not to_email or str(to_email).strip().lower() in ('not found', '', 'nan', 'none'):
        return ('NO_EMAIL', 'No valid email address')

    if not body or str(body).strip() == '':
        return ('FAILED', 'No message body')

    if dry_run:
        print(f"[DRY RUN] Would send email to: {to_email}")
        print(f"  Subject: {subject}")
        print(f"  Body preview: {str(body)[:100]}...")
        print(f"  Status: SIMULATED")
        return ('SIMULATED', '')

    try:
        if not sender_email or not sender_password:
            return ('FAILED', 'Missing sender credentials')

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()

        print(f"[SENT] Email sent to: {to_email}")
        return ('SENT', '')
    except Exception as e:
        print(f"[FAILED] Email to {to_email}: {str(e)}")
        return ('FAILED', str(e))


def send_all_outreach(df, dry_run=True, db_path=None):
    """
    Send outreach to all qualified influencers.

    For each row where filter_status == 'Passed':
    1. Check if already contacted (prevents duplicate outreach)
    2. Check if email is valid
    3. Check if email_pitch exists
    4. Send email (dry-run or real)

    Returns: list of dicts with keys:
      influencer_name, email, status, error_message, sent_date
    """
    from src.database import is_already_contacted, insert_outreach, init_db

    load_dotenv()
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    dry_run_env = os.getenv('DRY_RUN', 'True').lower() in ('true', '1', 'yes')
    if dry_run is None:
        dry_run = dry_run_env

    # Initialize the database
    if db_path:
        init_db(db_path)
    else:
        init_db()

    results = []

    counts = {
        'Total': 0,
        'Simulated': 0,
        'Sent': 0,
        'Failed': 0,
        'Skipped': 0,
        'No Email': 0,
        'Not Ready': 0
    }

    qualified_df = df[df['filter_status'] == 'Passed'] if 'filter_status' in df.columns else df
    counts['Total'] = len(qualified_df)

    for idx, row in qualified_df.iterrows():
        email = str(row.get('email', '')).strip()
        name = str(row.get('name', 'Unknown')).strip()
        pitch = str(row.get('email_pitch', '')).strip()
        dm = str(row.get('instagram_dm', '')).strip()

        status = ''
        error_message = ''
        sent_date = datetime.now().isoformat()

        # Check 1: Duplicate outreach prevention
        if email and email.lower() not in ('not found', '', 'nan', 'none') and is_already_contacted(email, db_path):
            status = 'SKIPPED_DUPLICATE'
            error_message = 'Already contacted'
            counts['Skipped'] += 1
            print(f"[SKIPPED] {name} ({email}) - Already contacted")

        # Check 2: No valid email
        elif not email or email.lower() in ('not found', '', 'nan', 'none'):
            status = 'NO_EMAIL'
            error_message = 'No valid email address'
            counts['No Email'] += 1
            print(f"[NO EMAIL] {name} - No valid email address")

        # Check 3: No message generated
        elif not pitch or pitch.lower() in ('', 'nan', 'none'):
            status = 'NOT_READY'
            error_message = 'No personalized message generated'
            counts['Not Ready'] += 1
            print(f"[NOT READY] {name} - No message generated")

        # Check 4: Send email
        else:
            subject = f"Collaboration Opportunity — AI Tools x {name}"
            status, error_message = send_email(
                email, subject, pitch, dry_run, sender_email, sender_password
            )

            if status == 'SIMULATED':
                counts['Simulated'] += 1
            elif status == 'SENT':
                counts['Sent'] += 1
            else:
                counts['Failed'] += 1

        # Insert outreach record into database
        try:
            outreach_record = {
                'influencer_id': int(idx) if idx is not None else 0,
                'email': email if email.lower() not in ('not found', 'nan', 'none') else '',
                'email_message': pitch,
                'instagram_dm': dm,
                'sent_date': sent_date,
                'status': status,
                'error_message': error_message
            }
            insert_outreach(outreach_record, db_path)
        except Exception as e:
            print(f"Warning: Could not insert outreach record for {name}: {e}")

        results.append({
            'influencer_name': name,
            'email': email,
            'status': status,
            'error_message': error_message,
            'sent_date': sent_date
        })

    # Print summary
    print("\n" + "=" * 50)
    print("📊 Outreach Summary")
    print("=" * 50)
    print(f"  Total Qualified: {counts['Total']}")
    print(f"  Simulated:       {counts['Simulated']}")
    print(f"  Sent:            {counts['Sent']}")
    print(f"  Failed:          {counts['Failed']}")
    print(f"  Skipped (Dup):   {counts['Skipped']}")
    print(f"  No Email:        {counts['No Email']}")
    print(f"  Not Ready:       {counts['Not Ready']}")
    print("=" * 50)

    return results
