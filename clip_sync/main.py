import pyperclip
import requests
import time
import sys
import argparse

def sync_clipboard(hub_url, interval):
    last_local = pyperclip.paste()
    last_remote_id = None

    print(f"🚀 Clipboard Sync Active")
    print(f"📡 Hub: {hub_url}")
    print(f"⏱️  Interval: {interval}s")
    print("Press Ctrl+C to stop.\n")

    while True:
        try:
            # --- STEP 1: PUSH (Local -> Hub) ---
            current_local = pyperclip.paste()
            if current_local != last_local:
                if current_local.strip():
                    requests.post(f"{hub_url}/api/paste", data=current_local, timeout=2)
                last_local = current_local
                print("📤 Pushed to Hub")

            # --- STEP 2: PULL (Hub -> Local) ---
            r = requests.get(f"{hub_url}/api/latest", timeout=2)
            if r.status_code == 200:
                data = r.json()
                remote_id = data.get('id')
                
                if remote_id != last_remote_id:
                    new_content = data.get('content')
                    if new_content != last_local:
                        pyperclip.copy(new_content)
                        last_local = new_content
                    
                    last_remote_id = remote_id
                    print("📥 Pulled from Hub")

        except Exception:
            pass

        time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description="Cross-platform Network Clipboard Sync")
    parser.add_argument("--hub", required=True, help="The URL of your Microbin hub (e.g., http://192.168.68.62:8081)")
    parser.add_argument("--interval", type=float, default=1.0, help="Sync interval in seconds")
    
    args = parser.parse_args()
    hub_url = args.hub.rstrip('/')
    sync_clipboard(hub_url, args.interval)

if __name__ == "__main__":
    main()
