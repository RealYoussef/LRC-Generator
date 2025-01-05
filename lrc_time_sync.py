import tkinter as tk
from tkinter import filedialog, messagebox
import os


class LRCTimeSync:
    def __init__(self, root, setup_menu_callback):
        self.root = root
        self.setup_menu_callback = setup_menu_callback

        # Setup the UI
        self.setup_ui()

    def setup_ui(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Set up menu
        self.setup_menu_callback()

        # Instruction label
        tk.Label(self.root, text="LRC Time Sync Tool", font=("Helvetica", 16, "bold")).pack(pady=10)

        # File selection button
        tk.Button(self.root, text="Load LRC File", command=self.load_lrc_file).pack(pady=10)

        # Text box to display and edit the LRC content
        self.lrc_text = tk.Text(self.root, width=80, height=20)
        self.lrc_text.pack(pady=10)

        # Sync button
        tk.Button(self.root, text="Sync Timings", command=self.sync_timings).pack(pady=10)

        # Save button
        tk.Button(self.root, text="Save LRC File", command=self.save_lrc_file).pack(pady=10)

    def load_lrc_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("LRC Files", "*.lrc")])
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                self.lrc_text.delete(1.0, tk.END)
                self.lrc_text.insert(tk.END, file.read())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load LRC file: {e}")

    def sync_timings(self):
        lines = self.lrc_text.get("1.0", tk.END).split("\n")
        synced_lines = []
        valid_intervals = [0.00, 0.20, 0.40, 0.60, 0.80]  # Valid intervals
    
        for line in lines:
            if line.startswith("[") and "]" in line:
                try:
                    # Extract the timestamp and the text
                    timestamp, text = line.split("]", 1)
                    minutes, seconds = map(float, timestamp[1:].split(":"))
                    full_seconds = int(seconds)
                    milliseconds = seconds - full_seconds
                    
                    # Find the closest valid interval
                    closest_interval = min(valid_intervals, key=lambda x: abs(x - milliseconds))
                    new_seconds = full_seconds + closest_interval
                    new_minutes = int(minutes)
                    
                    # If new_seconds reaches 60, adjust minutes and seconds
                    if new_seconds >= 60:
                        new_minutes += 1
                        new_seconds -= 60
                    
                    # Format the new timestamp
                    new_timestamp = f"[{new_minutes:02}:{new_seconds:05.2f}]"
                    synced_lines.append(f"{new_timestamp}{text}")
                except Exception:
                    synced_lines.append(line)  # If parsing fails, keep the line as is
            else:
                synced_lines.append(line)
    
        self.lrc_text.delete(1.0, tk.END)
        self.lrc_text.insert(tk.END, "\n".join(synced_lines))
        messagebox.showinfo("Success", "LRC timings have been synchronized!")


    def save_lrc_file(self):
        # Check if an LRC file has been loaded
        if not hasattr(self, 'file_path') or not self.file_path:
            default_filename = "output.lrc"
        else:
            # Extract the base name from the original file path
            default_filename = os.path.basename(self.file_path)
    
        # Prompt user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".lrc",
            initialfile=default_filename,
            filetypes=[("LRC Files", "*.lrc")]
        )
        if not file_path:
            return  # User cancelled save
    
        try:
            # Save the content of the LRC text box to the specified file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.lrc_text.get("1.0", tk.END))
            messagebox.showinfo("Success", f"LRC file saved at {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save LRC file: {e}")

