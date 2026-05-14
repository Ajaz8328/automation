#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check Azure DevOps work item types"""

import sys
import io
import requests
import base64

# Set UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ADO_ORG = "Test-Org-Azaz"
ADO_PROJECT = "Jupiter"
ADO_PAT = "2rCI990lWuLTfAqBDy05jPfqUVMpv9p1cz53ovQRoiOXtqtPeEnZJQQJ99CEACAAAAAAAAAAAAASAZDO1qiA"

# Encode PAT for Basic Auth
auth_string = f":{ADO_PAT}"
auth_bytes = auth_string.encode('ascii')
auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

headers = {
    "Authorization": f"Basic {auth_b64}",
    "Content-Type": "application/json"
}

print("\n[*] Checking Azure DevOps work item types...")
print(f"    Organization: {ADO_ORG}")
print(f"    Project: {ADO_PROJECT}\n")

# Get work item types
url = f"https://dev.azure.com/{ADO_ORG}/{ADO_PROJECT}/_apis/wit/workitemtypes?api-version=7.0"

try:
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        types = data.get('value', [])
        
        print(f"[+] Found {len(types)} work item types:\n")
        for wit in types:
            print(f"  - {wit.get('name')} (Reference: {wit.get('referenceName')})")
            print(f"    Description: {wit.get('description', 'N/A')}")
            print()
    else:
        print(f"[-] Failed: {response.status_code}")
        print(f"    Response: {response.text}")
        
except Exception as e:
    print(f"[-] Error: {e}")

# Made with Bob
