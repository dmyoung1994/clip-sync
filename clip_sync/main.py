import pyperclip
import requests
import time
import sys
import argparse
import subprocess
import os
import re

def sync_clipboard(hub_url, interval):
    print(f"[*] Starting Turbo Clip-Sync (Watchdog Mode)...")
    print(f"[*] Hub URL: {hub_url}")
    print(f"[*] Polling every {interval}s")
    print("Press Ctrl+C to stop.\n")
    
    hub_url = hub_url.rstrip('/')
    last_local = pyperclip.paste()
    
    # We track both the ID we are watching AND the ID we last saw on the hub
    last_known_hub_id = None
    last_local_content = last_local

    while True:
        try:
            # --- STEP 1: DISCOVERY (What is the latest thing on the hub?) ---
            # We use /list because it's the most reliable way to find the 'top' item
            discovery_resp = requests.get(f"{hub_url}/list", timeout=3)
            
            if discovery_resp.status_code == 200:
                # Extract the ID of the most recent paste from the HTML
                # Microbin list shows them as <a href="/raw/id">Text</a> or <a href="/upload/id">ID</a>
                match = re.search(r'href="/(?:raw|upload)/([a-zA-Z0-9-]+)"', discovery_resp.text)
                
                if match:
                    latest_hub_id = match.group(1)
                    
                    # If the hub has a new latest ID, we need to check its content
                    if latest_hub_id != last_known_hub_id:
                        print(f"[+] New item detected on hub: {latest_hub_id}")
                        last_known_hub_id = latest_hub_id
                        
                        # Immediately fetch the content of this new ID
                        remote_content = fetch_raw_content(hub_url, latest_hub_id)
                        
                        if remote_content and remote_content != last_local_content:
                            print(f"[+] REMOTE CHANGE! Syncing to local...")
                            pyperclip.copy(remote_content)
                            last_local_content = remote_content
                            last_local = remote_content # Sync local to match
                else:
                    pass # No pastes found yet
            
            # --- STEP 2: PUSH (Local -> Hub) ---
            # If the user copies something locally, we upload it
            current_local = pyperclip.paste()
            if current_local != last_local:
                print(f"[!] Local change detected. Uploading...")
                files = {'content': (None, current_local)}
                upload_resp = requests.post(f"{hub_url}/upload", files=files, allow_redirects=False, timeout=5)
                
                if upload_resp.status_code in [200, 301, 302]:
                    new_location = upload_resp.headers.get('Location', '')
                    match = re.search(r'/upload/([a-zA-Z0-9-]+)', new_location)
                    if match:
                        new_id = match.group(1)
                        print(f"[+] SUCCESS: Uploaded. New ID: {new_id}")
                        last_local = current_local
                        last_local_content = current_local
                        # We don't update last_known_hub_id yet; the next discovery cycle will catch it
                    else:
                        print(f"[!] Uploaded but couldn't parse ID from: {new_location}")
                else:
                    print(f"[!] Upload failed. Status: {upload_resp.status_code}")

        except Exception as e:
            print(f"[!] Loop Error: {e}")

        time.sleep(interval)

def fetch_raw_content(hub_url, paste_id):
    """Helper to get plain text from a paste ID."""
    try:
        url = f"{hub_url}/raw/{paste_id}"
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            return resp.text
    except:
        pass
    return None

def main():
    parser = argparse.ArgumentParser(description="Turbo Clip-Sync (Watchdog Mode)")
    parser.add_argument("--hub", required=True, help="The URL of your Microbin hub")
    parser.add_argument("--interval", type=float, default=0.25, help="Sync interval (seconds)")
    parser.add_argument("--daemon", action="store_true", help="Run in background mode")

    args = parser.parse_args()

    if args.daemon:
        if sys.platform == "win32":
            python_exe = sys.executable.replace("python.exe", "pythonw.exe")
            if not os.path.exists(python_exe): python_exe = "pythonw"
            cmd = [python_exe, __file__, "--hub", args.hub, "--interval", str(args.interval)]
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS)
            print("[+] Daemon started in background.")
            sys.exit(0)
        else:
            subprocess.Popen([sys.executable, __file__, "--hub", args.hub, "--interval", str(args.interval)], 
                             start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("[+] Daemon started in background.")
            sys.exit(0)

    try:
        sync_clipboard(args.hub, args.interval)
    except KeyboardInterrupt:
        print("\n[*] Exiting...")

if __name__ == "__main__":
    main()
