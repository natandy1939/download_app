import json
from pathlib import Path

# --- CONFIGURATION ---
VIDEO_DIR = Path(r'C:\Users\MAB\Desktop\download_app\download')
OUTPUT_FILE = Path('videos.json')
EXTENSIONS = {'.mp4', '.webm', '.ogg', '.mkv'}

def generate_video_list():
    """Scans the folder and updates the JSON file."""
    videos = []
    
    if not VIDEO_DIR.exists():
        print(f"[-] Directory not found: {VIDEO_DIR}")
        return

    for file_path in VIDEO_DIR.iterdir():
        # Only process files that match our exact video extensions
        if file_path.is_file() and file_path.suffix.lower() in EXTENSIONS:
            videos.append({
                "title": file_path.stem,
                "src": f"download/{file_path.name}"
            })
    
    videos = sorted(videos, key=lambda k: k['title'])
    
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(videos, f, indent=4)
        print(f"[+] JSON Updated: {len(videos)} videos found.")
    except PermissionError:
        print("[-] PermissionError: Could not write to the JSON file right now.")

def main():
    print(f"[*] Running one-time JSON scan for {VIDEO_DIR}...")
    
    # Ensure directory exists before scanning
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    
    # Execute the scan exactly once
    generate_video_list()
    
    print("[*] Job complete. Terminating script.")

if __name__ == "__main__":
    main()