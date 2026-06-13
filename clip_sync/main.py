import pyperclip
import requests
import time
import sys
import argparse
import subprocess
import os
import re

def sync_clipboard(hub_url, interval):
    print(f"[*] Starting Turbo Clip-Sync...")
    print(f"[*] Hub URL: {hub_url}")
    print(f"[*] Polling every {interval}s")
    print("Press Ctrl+C to stop.\n")
    
    hub_url = hub_url.rstrip('/')
    last_local = pyperclip.paste()
    last_remote_id = None

    while True:
        try:
            # 1. Check Local Clipboard
            current_local = pyperclip.paste()

            if current_local != last_local:
                # If local has changed, upload it using multipart/form-data
                # This is the most reliable way for Microbin
                print("[+] Local change detected. Uploading...")
                files = {'content': (None, current_local)}
                response = requests.post(f"{hub_url}/upload", files=files, allow_redirects=False, timeout=5)
                
                if response.status_code in [200, 301, 302]:
                    new_location = response.headers.get('Location', '')
                    if new_location:
                        # The location is /upload/<id>
                        match = re.search(r'/upload/([a-zA-Z0-9-]+)', new_location)
                        if match:
                            last_remote_id = match.group(1)
                            print(f"[+] SUCCESS: Uploaded. New ID: {last_remote_id}")
                        else:
                            # Fallback for other redirect styles
                            last_remote_id = new_location.split('/')[-1]
                            print(f"[+] SUCCESS: Uploaded. New ID: {last_remote_id}")
                        
                        last_local = current_local
                    else:
                        print(f"[!] Uploaded, but no location header found.")
                else:
                    print(f"[!] Upload failed. Status: {response.status_code}")
                    print(f"    Response: {response.text[:100]}")

            # 2. Check Remote Clipboard (if we have an active ID)
            if last_remote_id:
                # Use the /raw/<id> endpoint which returns plain text
                remote_url = f"{hub_url}/raw/{last_remote_id}"
                remote_resp = requests.get(remote_url, timeout=3)
                
                if remote_resp.status_code == 200:
                    remote_content = remote_resp.text
                    
                    # Check if remote content is different from our local
                    if remote_content != last_local:
                        print(f"[+] REMOTE CHANGE! Updating local clipboard.")
                        pyperclip.copy(remote_content)
                        last_local = remote_content
                elif remote_resp.status_code == 404:
                    # If the paste expired or was deleted, reset the tracker
                    last_remote_id = None
                else:
                    # Other errors (timeout, etc)
                    pass

        except Exception as e:
            print(f"[!] Error in loop: {e}")

        time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description="Turbo Clip-Sync (0.25s Polling)")
    parser.add_argument("--hub", required=True, help="The URL of your Microbin hub")
    parser.add_argument("--interval", type=float, default=0.25, help="Sync interval (default: 0.25s)")
    parser.add_argument("--daemon", action="store_true", help="Run in background mode")

    args = parser.parse_args()

    if args.daemon:
        print("[*] Spawning daemon process...")
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
