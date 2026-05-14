#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""List available tickets in Zammad"""

import sys
import io
import requests
import json

# Set UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ZAMMAD_URL = "https://test-azaz.zammad.com"
ZAMMAD_TOKEN = "K4vz0Qh-6RPURKvIf0EDRubgjkYqLqQYEwlgjUczk8zT5OPtf4DEL5TGB21gXGso"

headers = {
    "Authorization": f"Token token={ZAMMAD_TOKEN}",
    "Content-Type": "application/json"
}

print("\n[*] Fetching tickets from Zammad...")
print(f"    URL: {ZAMMAD_URL}")

try:
    # Try to get tickets
    response = requests.get(
        f"{ZAMMAD_URL}/api/v1/tickets",
        headers=headers,
        timeout=10
    )
    
    print(f"\n[*] Response Status: {response.status_code}")
    
    if response.status_code == 200:
        tickets = response.json()
        print(f"[+] Found {len(tickets)} tickets\n")
        
        for ticket in tickets[:10]:  # Show first 10
            print(f"Ticket #{ticket.get('id')}: {ticket.get('title')}")
            print(f"  State: {ticket.get('state')}")
            print(f"  Priority: {ticket.get('priority')}")
            print()
    else:
        print(f"[-] Failed: {response.text}")
        
except Exception as e:
    print(f"[-] Error: {e}")

# Made with Bob
