import customtkinter as ctk
import yt_dlp
import os
import threading
import re

# ================= Configuration =================
FILE_NAME = "link.txt"
DOWNLOAD_DIR = r"C:\Users\MAB\Desktop\download_app\download" 
# =================================================

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class OneTimeYTDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Hide the window immediately before anything else loads
        self.withdraw()

        self.title("YT Downloader")
        self.geometry("550x350")
        self.eval('tk::PlaceWindow . center')
        self.protocol("WM_DELETE_WINDOW", self.on_close_window)

        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

        self.current_url = ""
        self.selected_quality = ctk.StringVar(value="Fetching...")

        self.setup_ui()
        
        # FIX: Wait until the mainloop actually starts before checking the file
        self.after(100, self.check_file_once)

    def setup_ui(self):
        self.url_label = ctk.CTkLabel(self, text="Link Found:", font=("Arial", 12, "bold"))
        self.url_label.pack(pady=(20, 5))

        self.url_display = ctk.CTkLabel(self, text="", text_color="gray", font=("Arial", 10))
        self.url_display.pack(pady=(0, 15))

        self.quality_menu = ctk.CTkOptionMenu(self, variable=self.selected_quality, values=["Fetching..."], state="disabled")
        self.quality_menu.pack(pady=10)

        self.download_btn = ctk.CTkButton(self, text="Download Video", command=self.start_download, fg_color="green", hover_color="darkgreen", state="disabled")
        self.download_btn.pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(20, 5))

        self.progress_label = ctk.CTkLabel(self, text="0% | Speed: ~ | ETA: ~", text_color="gray")
        self.progress_label.pack()

        self.status_label = ctk.CTkLabel(self, text="Fetching metadata...", text_color="yellow", font=("Arial", 14, "bold"))
        self.status_label.pack(pady=10)

    def update_ui(self, widget, **kwargs):
        self.after(0, lambda: widget.configure(**kwargs))

    # --- ONE-TIME CHECK LOGIC ---
    def check_file_once(self):
        if os.path.exists(FILE_NAME):
            try:
                with open(FILE_NAME, "r") as f:
                    raw_data = f.read().strip()
                
                if raw_data:
                    # Grab the first line only to drop hidden \n characters
                    url = raw_data.split('\n')[0].strip()
                    
                    if "youtube.com" in url or "youtu.be" in url:
                        # FIX: We DO NOT clear the file here anymore. 
                        # We wait until the app exits to prevent link loss on errors.
                        self.current_url = url
                        self.show_app_and_fetch()
                        return # Stop here so we don't destroy the app
            except Exception as e:
                pass 
        
        # If no valid link was found, terminate the app immediately
        self.destroy()

    def show_app_and_fetch(self):
        self.progress_bar.set(0)
        self.update_ui(self.url_display, text=self.current_url if len(self.current_url) < 60 else self.current_url[:57] + "...")
        self.update_ui(self.status_label, text="Fetching qualities... Please wait.", text_color="yellow")
        self.update_ui(self.quality_menu, state="disabled", values=["Fetching..."])
        self.update_ui(self.download_btn, state="disabled")
        self.update_ui(self.progress_label, text="")
        
        # Pop the UI open safely
        self.deiconify()
        threading.Thread(target=self.fetch_qualities, daemon=True).start()

    def fetch_qualities(self):
        ydl_opts = {
            'quiet': True, 
            'no_warnings': True,
            'ignoreerrors': True,
            'no_color': True,
            'socket_timeout': 10,
            'source_address': '0.0.0.0', # Force IPv4
            'cachedir': False # Disable SQLite locks
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.current_url, download=False)
                
                if not info:
                    raise ValueError("yt-dlp returned None. The video might be private or region-locked.")

                resolutions = set()
                for f in info.get('formats', []):
                    if f.get('vcodec') != 'none' and f.get('height'):
                        resolutions.add(f.get('height'))
                
                sorted_res = sorted(list(resolutions), reverse=True)
                formatted_res = [f"{res}p" for res in sorted_res]

                if not formatted_res:
                    raise ValueError("No viable video formats found.")

                self.update_ui(self.quality_menu, values=formatted_res, state="normal")
                self.after(0, lambda: self.selected_quality.set(formatted_res[0]))
                self.update_ui(self.download_btn, state="normal")
                self.update_ui(self.status_label, text="Ready to download.", text_color="green")
                
        except Exception as e:
            print(f"[ERROR] Fetch failed: {e}")
            self.update_ui(self.status_label, text="Error fetching info. Invalid link?", text_color="red")
            # Give the user a moment to see the error, then close and clean up
            self.after(3000, self.finish_and_exit)

    # --- DOWNLOAD LOGIC ---
    def start_download(self):
        quality = self.selected_quality.get()
        self.update_ui(self.status_label, text=f"Downloading {quality}...", text_color="yellow")
        self.update_ui(self.download_btn, state="disabled")
        self.update_ui(self.quality_menu, state="disabled")
        
        threading.Thread(target=self.download_video, args=(quality,), daemon=True).start()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total > 0:
                percent = d.get('downloaded_bytes', 0) / total
                self.after(0, lambda p=percent: self.progress_bar.set(p))
            
            speed = d.get('_speed_str', '~')
            eta = d.get('_eta_str', '~')
            raw_percent = d.get('_percent_str', '0%')
            clean_percent = re.sub(r'\x1b\[[0-9;]*m', '', raw_percent).strip()

            status_text = f"{clean_percent} | Speed: {speed} | ETA: {eta}"
            self.update_ui(self.progress_label, text=status_text)
            
        elif d['status'] == 'finished':
            self.after(0, lambda: self.progress_bar.set(1))
            self.update_ui(self.progress_label, text="100% | Download complete.")
            self.update_ui(self.status_label, text="Merging audio/video... (Please wait)", text_color="yellow")

    def download_video(self, quality):
        height = quality.replace("p", "")
        
        ydl_opts = {
            'format': f'bestvideo[ext=mp4][height<={height}]+bestaudio[ext=m4a]/best[ext=mp4][height<={height}]/best',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'quiet': True,
            'noprogress': True,
            'socket_timeout': 15,
            'source_address': '0.0.0.0', 
            'cachedir': False, 
            'progress_hooks': [self.progress_hook]
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.current_url])
            
            self.update_ui(self.status_label, text="Success! Saved to folder.", text_color="#00FF00")
            self.after(2000, self.finish_and_exit)

        except Exception as e:
            print(f"[ERROR] Download failed: {e}")
            self.update_ui(self.status_label, text="Download failed!", text_color="red")
            self.update_ui(self.download_btn, state="normal")

    # --- CLEANUP LOGIC ---
    def on_close_window(self):
        self.finish_and_exit()

    def finish_and_exit(self):
        try:
            # FIX: File is cleared ONLY when the app is actually terminating.
            open(FILE_NAME, "w").close()
        except Exception:
            pass
        
        # Completely terminate the application
        self.destroy()

if __name__ == "__main__":
    app = OneTimeYTDownloader()
    app.mainloop()