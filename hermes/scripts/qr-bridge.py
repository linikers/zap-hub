#!/usr/bin/env python3
"""QR Bridge - starts WhatsApp bridge and generates QR code as PNG"""
import subprocess
import sys
import os
import re
import json
import time

sys.path.insert(0, "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages")
import qrcode
from qrcode.image.pil import PilImage

BRIDGE_DIR = "/usr/local/lib/hermes-agent/scripts/whatsapp-bridge"
SESSION_DIR = "/root/.hermes/whatsapp/session"
OUTPUT_QR = "/root/.hermes/scripts/whatsapp-qr.png"
os.makedirs(SESSION_DIR, exist_ok=True)

# Start the bridge
proc = subprocess.Popen(
    ["node", "bridge.js", "--port", "3000", "--session", SESSION_DIR, "--mode", "self-chat"],
    cwd=BRIDGE_DIR,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)

print("Bridge started, waiting for QR code...")

# Read output looking for QR data
qr_regex = re.compile(r'[\x00-\x7F]{10,}')  # rough pattern for QR data
buf = ""
qr_data = None

for line in iter(proc.stdout.readline, ""):
    print(line, end="", flush=True)
    
    # The QR data is passed to qrcode-terminal library
    # We need a different approach - patch the bridge
    
    if "Scan this QR code" in line:
        print("\n[QR CODE GENERATED - check the output above]")
    
    if "Waiting for scan" in line:
        print("\n[READY FOR SCAN]")
    
    if "WhatsApp connected" in line:
        print("\n[CONNECTED!]")
        break
    
    if "Failed to connect" in line or "loggedOut" in line:
        print("\n[ERROR]")
        break

# Keep running
proc.wait()
