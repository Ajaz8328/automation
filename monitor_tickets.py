#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ticket Monitor - Continuous monitoring for Zammad tickets
This script is accessed by Bob through GitHub connector in Context Studio
"""

import sys
import io
import requests
import subprocess
import time
import os
from datetime import datetime

# Set UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Configuration
ZAMMAD_URL = "https://test-azaz.zammad.com"
ZAMMAD_TOKEN = "K4vz0Qh-6RPURKvIf0EDRubgjkYqLqQYEwlgjUczk8zT5OPtf4DEL5TGB21gXGso"

# Track processed tickets
processed_tickets = set()

def log_event(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def get_new_tickets():
    """Check for new Grafana alert tickets in Zammad"""
    log_event("Checking for new tickets...")
    
    headers = {
        "Authorization": f"Token token={ZAMMAD_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # Search for Grafana alert tickets
        response = requests.get(
            f"{ZAMMAD_URL}/api/v1/tickets/search?query=title:Grafana",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            tickets = data.get('assets', {}).get('Ticket', {})
            
            new_tickets = []
            for ticket_id, ticket in tickets.items():
                tid = int(ticket_id)
                if tid not in processed_tickets:
                    new_tickets.append({
                        'id': tid,
                        'title': ticket.get('title', 'N/A'),
                        'created_at': ticket.get('created_at', 'N/A')
                    })
                    
            return new_tickets
        else:
            log_event(f"Failed to fetch tickets: {response.status_code}")
            return []
            
    except Exception as e:
        log_event(f"Error fetching tickets: {e}")
        return []

def process_ticket(ticket):
    """Process a ticket using the automation script"""
    ticket_id = ticket['id']
    log_event(f"Processing ticket #{ticket_id}: {ticket['title']}")
    
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        automation_script = os.path.join(script_dir, 'zammad_ado_automation.py')
        
        # Check if running on Windows
        if sys.platform == 'win32':
            python_exe = r"C:\Users\AzazShaik\Downloads\python.exe"
        else:
            python_exe = "python3"
        
        # Run the automation script
        log_event(f"Executing automation for ticket #{ticket_id}...")
        result = subprocess.run(
            [python_exe, automation_script, str(ticket_id)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=script_dir
        )
        
        if result.returncode == 0:
            log_event(f"[SUCCESS] Ticket #{ticket_id} processed successfully")
            log_event(f"Output: {result.stdout[:200]}...")  # Show first 200 chars
            processed_tickets.add(ticket_id)
            return True
        else:
            log_event(f"[FAILED] Ticket #{ticket_id} processing failed")
            log_event(f"Error: {result.stderr[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        log_event(f"[TIMEOUT] Ticket #{ticket_id} processing timed out")
        return False
    except Exception as e:
        log_event(f"[ERROR] Exception processing ticket #{ticket_id}: {e}")
        return False

def main():
    """Main monitoring loop"""
    print("\n" + "="*60)
    print("  BOB AGENT - Zammad Ticket Monitor")
    print("  Integrated with Context Studio via GitHub Connector")
    print("="*60 + "\n")
    
    log_event("Starting continuous monitoring...")
    log_event("Monitoring Zammad for Grafana alert tickets")
    log_event("Checking every 30 seconds")
    log_event("Press Ctrl+C to stop\n")
    
    check_count = 0
    
    while True:
        try:
            check_count += 1
            log_event(f"Check #{check_count}")
            
            # Get new tickets
            new_tickets = get_new_tickets()
            
            if new_tickets:
                log_event(f"Found {len(new_tickets)} new ticket(s) to process")
                
                for ticket in new_tickets:
                    process_ticket(ticket)
                    time.sleep(2)  # Small delay between tickets
                    
                log_event(f"Processed {len(new_tickets)} ticket(s)")
            else:
                log_event("No new tickets found")
            
            log_event(f"Total tickets processed so far: {len(processed_tickets)}")
            log_event("Waiting 30 seconds before next check...\n")
            time.sleep(30)
            
        except KeyboardInterrupt:
            log_event("\n\nShutting down gracefully...")
            log_event(f"Total tickets processed: {len(processed_tickets)}")
            log_event("Agent stopped by user")
            break
            
        except Exception as e:
            log_event(f"Unexpected error: {e}")
            log_event("Continuing monitoring after 30 seconds...")
            time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_event(f"Fatal error: {e}")
        sys.exit(1)

# Made with Bob
