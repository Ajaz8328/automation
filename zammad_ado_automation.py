#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zammad to Azure DevOps Automation Script
Processes Zammad tickets and creates Azure DevOps bugs
"""

import sys
import io
import requests
import json
import base64
from datetime import datetime, timedelta

# Set UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Configuration
ZAMMAD_URL = "https://test-azaz.zammad.com"
ZAMMAD_TOKEN = "K4vz0Qh-6RPURKvIf0EDRubgjkYqLqQYEwlgjUczk8zT5OPtf4DEL5TGB21gXGso"
LOKI_URL = "http://localhost:3100"
ADO_ORG = "Test-Org-Azaz"
ADO_PROJECT = "Jupiter"
ADO_PAT = "2rCI990lWuLTfAqBDy05jPfqUVMpv9p1cz53ovQRoiOXtqtPeEnZJQQJ99CEACAAAAAAAAAAAAASAZDO1qiA"

def get_zammad_ticket(ticket_id):
    """Fetch ticket from Zammad"""
    print(f"\n[*] Fetching Zammad ticket #{ticket_id}...")
    
    headers = {
        "Authorization": f"Token token={ZAMMAD_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{ZAMMAD_URL}/api/v1/tickets/{ticket_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            ticket = response.json()
            print(f"[+] Ticket fetched: {ticket.get('title', 'N/A')}")
            
            # Check for severity in custom fields or article body
            severity = "N/A"
            if 'severity' in ticket:
                severity = ticket.get('severity')
            elif 'priority' in ticket:
                severity = ticket.get('priority')
            
            print(f"    Severity: {severity}")
            print(f"    State: {ticket.get('state', 'N/A')}")
            return ticket
        else:
            print(f"[-] Failed to fetch ticket: {response.status_code}")
            print(f"    Response: {response.text}")
            return None
    except Exception as e:
        print(f"[-] Error fetching ticket: {e}")
        return None

def get_ticket_articles(ticket_id):
    """Get ticket articles and playbook"""
    print(f"\n[*] Fetching ticket articles...")
    
    headers = {
        "Authorization": f"Token token={ZAMMAD_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{ZAMMAD_URL}/api/v1/ticket_articles/by_ticket/{ticket_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            articles = response.json()
            print(f"[+] Found {len(articles)} articles")
            
            # Look for playbook
            for article in articles:
                if article.get('attachments'):
                    for att in article['attachments']:
                        if 'playbook' in att.get('filename', '').lower():
                            print(f"    [PLAYBOOK] Found: {att['filename']}")
            
            return articles
        else:
            print(f"[-] Failed to fetch articles: {response.status_code}")
            return []
    except Exception as e:
        print(f"[-] Error fetching articles: {e}")
        return []

def query_loki_logs(time_range_hours=1):
    """Query error logs from Loki"""
    print(f"\n[*] Querying Loki for error logs (last {time_range_hours}h)...")
    
    # Calculate timestamps in nanoseconds
    now = datetime.now()
    start_time = now - timedelta(hours=time_range_hours)
    start_ns = int(start_time.timestamp() * 1e9)
    end_ns = int(now.timestamp() * 1e9)
    
    params = {
        "query": '{job="sample-app"} | json | level="error"',
        "start": start_ns,
        "end": end_ns,
        "limit": 100
    }
    
    try:
        response = requests.get(
            f"{LOKI_URL}/loki/api/v1/query_range",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('data', {}).get('result', [])
            
            log_count = sum(len(r.get('values', [])) for r in results)
            print(f"[+] Found {log_count} error logs")
            
            # Format logs
            logs = []
            for stream in results:
                for timestamp, log in stream.get('values', []):
                    ts = datetime.fromtimestamp(int(timestamp) / 1e9)
                    logs.append(f"[{ts.isoformat()}] {log}")
            
            return logs[:20]  # Return first 20 logs
        else:
            print(f"[!] Loki query failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"[!] Loki connection failed (this is OK if Loki is not running): {e}")
        return []

def create_ado_bug(ticket, logs):
    """Create issue in Azure DevOps"""
    print(f"\n[*] Creating issue in Azure DevOps...")
    
    # Prepare bug description
    log_summary = "\n".join(logs[:10]) if logs else "No error logs found (Loki may not be running)"
    
    description = f"""<div>
<h3>Ticket Information</h3>
<ul>
<li><strong>Ticket ID:</strong> #{ticket.get('id')}</li>
<li><strong>Title:</strong> {ticket.get('title')}</li>
<li><strong>Priority:</strong> {ticket.get('priority')}</li>
<li><strong>Created:</strong> {ticket.get('created_at')}</li>
</ul>

<h3>Error Logs</h3>
<pre>{log_summary}</pre>

<p><strong>Source:</strong> Automated from Zammad ticket #{ticket.get('id')}</p>
</div>"""
    
    # Create JSON Patch document
    document = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": f"Issue from Zammad Ticket #{ticket.get('id')}: {ticket.get('title')}"
        },
        {
            "op": "add",
            "path": "/fields/System.Description",
            "value": description
        },
        {
            "op": "add",
            "path": "/fields/Microsoft.VSTS.Common.Severity",
            "value": "2 - High"
        },
        {
            "op": "add",
            "path": "/fields/System.Tags",
            "value": f"zammad; automated; ticket-{ticket.get('id')}"
        }
    ]
    
    # Encode PAT for Basic Auth
    auth_string = f":{ADO_PAT}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/json-patch+json"
    }
    
    url = f"https://dev.azure.com/{ADO_ORG}/{ADO_PROJECT}/_apis/wit/workitems/$Issue?api-version=7.0"
    
    try:
        response = requests.post(url, json=document, headers=headers, timeout=15)
        
        if response.status_code == 200:
            bug = response.json()
            bug_id = bug.get('id')
            bug_url = bug.get('_links', {}).get('html', {}).get('href', '')
            
            print(f"[+] Issue created successfully!")
            print(f"    Issue ID: {bug_id}")
            print(f"   URL: {bug_url}")
            
            return {"id": bug_id, "url": bug_url}
        else:
            print(f"[-] Failed to create issue: {response.status_code}")
            print(f"    Response: {response.text}")
            return None
    except Exception as e:
        print(f"[-] Error creating issue: {e}")
        return None

def update_zammad_ticket(ticket_id, bug_info):
    """Update Zammad ticket with bug information"""
    print(f"\n[*] Updating Zammad ticket...")
    
    headers = {
        "Authorization": f"Token token={ZAMMAD_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # Update ticket state
        response = requests.put(
            f"{ZAMMAD_URL}/api/v1/tickets/{ticket_id}",
            json={"state": "pending close"},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"[+] Ticket state updated to 'pending close'")
        else:
            print(f"[!] Failed to update state: {response.status_code}")
        
        # Add article with bug link
        article_body = f"""[+] Issue created in Azure DevOps

**Issue Details:**
- Issue ID: {bug_info['id']}
- URL: {bug_info['url']}

**Actions Taken:**
- Analyzed ticket information
- Queried error logs from Loki
- Created detailed issue in Azure DevOps
- Tagged for tracking

The issue has been escalated to the development team.
"""
        
        response = requests.post(
            f"{ZAMMAD_URL}/api/v1/ticket_articles",
            json={
                "ticket_id": int(ticket_id),
                "body": article_body,
                "type": "note",
                "internal": False
            },
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            print(f"[+] Article added to ticket with bug link")
        else:
            print(f"[!] Failed to add article: {response.status_code}")
            
    except Exception as e:
        print(f"[-] Error updating ticket: {e}")

def process_ticket(ticket_id):
    """Main automation workflow"""
    print(f"\n{'='*60}")
    print(f"[START] Zammad to ADO Automation")
    print(f"        Ticket ID: {ticket_id}")
    print(f"{'='*60}")
    
    # Step 1: Fetch ticket
    ticket = get_zammad_ticket(ticket_id)
    if not ticket:
        print("\n[-] Automation failed: Could not fetch ticket")
        return False
    
    # Step 2: Get articles
    articles = get_ticket_articles(ticket_id)
    
    # Step 3: Query logs (optional - will continue even if Loki is not available)
    logs = query_loki_logs(time_range_hours=1)
    
    # Step 4: Create issue
    bug_info = create_ado_bug(ticket, logs)
    if not bug_info:
        print("\n[-] Automation failed: Could not create issue")
        return False
    
    # Step 5: Update ticket
    update_zammad_ticket(ticket_id, bug_info)
    
    print(f"\n{'='*60}")
    print(f"[SUCCESS] Automation completed successfully!")
    print(f"{'='*60}")
    print(f"\n[SUMMARY]")
    print(f"   Ticket: #{ticket_id}")
    print(f"   Issue: #{bug_info['id']}")
    print(f"   URL: {bug_info['url']}")
    print(f"   Logs analyzed: {len(logs)}")
    print(f"\n[DONE] Check Azure DevOps and Zammad to see the results!")
    
    return True

if __name__ == "__main__":
    import sys
    
    # Get ticket ID from command line or use default
    ticket_id = sys.argv[1] if len(sys.argv) > 1 else "53030"
    
    print("\n" + "="*60)
    print("  Zammad to Azure DevOps Automation")
    print("  Bobathon Challenge - Context Studio Integration")
    print("="*60)
    
    success = process_ticket(ticket_id)
    
    if success:
        print("\n[+] Automation completed successfully!")
        sys.exit(0)
    else:
        print("\n[-] Automation failed!")
        sys.exit(1)

# Made with Bob
