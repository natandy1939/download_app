import subprocess
import time
import sys
import os

def main():
    # 1. Start the local server in the background (Non-blocking)
    # We add "--bind", "0.0.0.0" so it's accessible via your IP (192.168.11.114)
    print("[*] Starting local UI server on port 8000 (Global Access)...")
    
    # Optional: Set this to the folder where index.html is
    # web_dir = r"C:\Users\MAB\Desktop\download_app\web_ui"
    
    server_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8000", "--bind", "0.0.0.0"],
        # cwd=web_dir  
    )

    # 2. Your existing master execution loop
    scripts = ["watcher.py", "downgui.py", "json_updater.py"]
    print("[*] Starting the master execution loop. Press Ctrl+C to stop.")
    
    try:
        while True:
            for script in scripts:
                # Check if file exists before running to avoid errors
                if not os.path.exists(script):
                    print(f"[!] Error: {script} not found in current directory.")
                    continue

                print(f"[*] Running {script}...")
                result = subprocess.run([sys.executable, script])
                
                if result.returncode != 0:
                    print(f"[!] Warning: {script} exited with code {result.returncode}")
                
                time.sleep(0.1)
                
            print("[+] Cycle complete. Looping back...\n" + "-"*40)
            
    except KeyboardInterrupt:
        print("\n[-] Execution terminated by user. Exiting.")
    finally:
        # 3. Clean up the server when you close the main script
        print("[*] Shutting down local server...")
        server_process.terminate()
        # Give it a moment to release the port
        server_process.wait()
        sys.exit(0)

if __name__ == "__main__":
    main()