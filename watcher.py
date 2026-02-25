import pyperclip
import time
import sys

# The sequence we are looking for
HANDSHAKE = "!{video}"

def main():
    print(f"Monitoring clipboard for {HANDSHAKE} every 250ms...")
    
    # We initialize this as empty
    last_clipboard = ""

    while True:
        try:
            current_clipboard = pyperclip.paste()
            
            # 1. Check if the clipboard changed
            # 2. Check if it starts with our secret sequence
            if current_clipboard != last_clipboard and current_clipboard.startswith(HANDSHAKE):
                
                # Extract only the link (remove the !{video} part)
                clean_link = current_clipboard.replace(HANDSHAKE, "")
                
                print(f"\n[+] Verified sequence found!")
                print(f"[+] Saving: {clean_link}")
                
                with open("link.txt", "a") as f:
                    f.write(clean_link + "\n")
                
                # Clear the clipboard so it doesn't get stuck
                pyperclip.copy("")
                print("[i] Clipboard cleared.")
                
                print("[i] Job finished. Terminating script forever...")
                break  # This stops the while loop and ends the script
                
            else:
                # Update last_clipboard normally if we didn't process anything
                last_clipboard = current_clipboard
            
            # Sleep for 250ms
            time.sleep(0.25)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
        # Catch occasional pyperclip read errors so the script doesn't crash
        except Exception as e:
            time.sleep(0.25)

if __name__ == "__main__":
    main()