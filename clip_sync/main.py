import pyperclip
import requests
import time
import sys
import argparse
import subprocess
import os
import re

def sync_clipboard(hub_url, interval):
    print(f"[*] Starting clip-sync daemon...")
    print(f"[*] Hub URL: {hub_url}")
    print(f"[*] Interval: {interval}s")
    
    # Ensure hub_url doesn't end with a slash for easier joining
    hub_url = hub_url.rstrip('/')
    
    last_local = pyperclip.paste()
    last_remote_id = None

    while True:
        try:
            # 1. Check Local Clipboard
            current_local = pyperclip.paste()

            # If local has changed, upload it
            if current_local != last_local:
                print(f"[+] Local change detected. Uploading...")
                # Microbin POST /upload takes 'content' as a form field
                response = requests.post(f"{hub_url}/upload", data={'content': current_local}, allow_redirects=False)
                
                if response.status_code in [200, 301, 302]:
                    # Get the new location from the header (e.g., /upload/abc123)
                    new_location = response.headers.get('Location')
                    if new_location:
                        # The location might be relative, so we handle it
                        if new_location.startswith('/'):
                            # Convert '/upload/id' to the actual paste path if needed
                            # Microbin usually redirects to /paste/id or similar
                            # We'll normalize it to the ID part
                            match = re.search(r'/upload/([a-zA-Z0-9]+)', new_location)
                            if match:
                                last_remote_id = match.group(1)
                                print(f"[+] Upload successful. New ID: {last_remote_id}")
                            else:
                                # Fallback if redirect is to the paste directly
                                last_remote_id = new_location.split('/')[-1]
                                print(f"[+] Upload successful. New ID: {last_remote_id}")
                        
                        last_local = current_local
                    else:
                        print(f"[!] Uploaded, but no location header found.")
                else:
                    print(f"[!] Upload failed. Status: {response.status_code}")

            # 2. Check Remote Clipboard
            if last_remote_id:
                # We try to fetch the raw content of the last known remote ID.
                # In Microbin, we can often get the raw content via /api/v1/paste/<id>
                # or by appending '.txt' or similar to the URL.
                # Let's try the most common API pattern.
                remote_url = f"{hub_url}/api/v1/paste/{last_remote_id}"
                
                # Try with JSON header first
                remote_resp = requests.get(remote_url, headers={"Accept": "application/json"}, timeout=5)
                
                remote_content = None
                if remote_resp.status_code == 200:
                    try:
                        data = remote_resp.json()
                        remote_content = data.get('content')
                    except:
                        pass
                
                # Fallback: if JSON failed, try getting it as plain text via the paste URL
                if not remote_content:
                    remote_resp = requests.get(f"{hub_url}/paste/{last_remote_id}", timeout=5)
                    if remote_resp.status_code == 200:
                        # If it's a webpage, we'll have to be smarter, 
                        # but Microbin usually serves raw text if requested correctly
                        remote_content = remote_resp.text

                if remote_content and remote_content != last_local:
                    # Clean up potential HTML if the fallback returned a page
                    if "<!DOCTYPE html>" in remote_content:
                        # This is a failure of our API detection; we'll log it.
                        print("[!] Warning: Received HTML instead of text. API endpoint might be wrong.")
                    else:
                        print(f"[+] Remote change detected! Updating local clipboard.")
                        pyperclip.copy(remote_content)
                        last_local = remote_content
                        # We don't update last_remote_id here because we want to keep watching this ID
                        # unless a new upload happens.

        except Exception as e:
            print(f"[!] Error in loop: {e}")

        time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description="Cross-platform Network Clipboard Sync")
    parser.add_argument("--hub", required=True, help="The URL of your Microbin hub (e.g., http://192.168.68.62:8081)")
    parser.add_argument("--interval", type=int, default=5, help="Sync interval in seconds (default: 5)")
    parser.add_argument("--daemon", action="store_true", help="Run in background mode")

    args = parser.parse_args()

    if args.daemon:
        print("[*] Spawning daemon process...")
        # For Windows, use pythonw to run without a console window
        # For Unix, use start_new_session to detach
        if sys.platform == "win32":
            # Find pythonw.exe path
            python_exe = sys.executable.replace("python.exe", "pythonw.exe")
            if not os.path.exists(python_exe):
                # If pythonw isn't in the same dir, try just 'pythonw'
                python_exe = "pythonw"
                
            cmd = [python_exe, __file__, "--hub", args.hub, "--interval", str(args.interval)]
            try:
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS)
                print("[+] Daemon started in background. You can close this window.")
                sys.exit(0)
            except Exception as e:
                print(f"[!] Failed to spawn daemon: {e}")
                sys.exit(1)
        else:
            # Unix/macOS: use start_new_session to fully detach
            try:
                subprocess.Popen([sys.executable, __file__, "--hub", args.hub, "--interval", str(args.interval)], 
                                 start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("[+] Daemon started in background. You can close this window.")
                sys.exit(0)
            except Exception as e:
                print(f"[!] Failed to spawn daemon: {e}")
                sys.exit(1)

    try:
        sync_clipboard(args.hub, args.interval)
    except KeyboardInterrupt:
        print("\n[*] Exiting...")

if __name__ == "__main__":
    main()
