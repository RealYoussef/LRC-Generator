import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re


class LRCTimingAdjuster:
    def __init__(self, root, setup_menu_callback):
        self.root = root
        self.root.title("LRC Timing Adjuster")
        self.root.geometry("800x900")

        # Setup the shared menu
        self.setup_menu_callback = setup_menu_callback
        self.setup_menu_callback()

        self.lrc_lines = []  # Store LRC file lines
        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self.root, text="LRC Timing Adjuster", font=("Helvetica", 18)).pack(pady=10)

        # Add controls for loading LRC file
        ttk.Button(self.root, text="Load LRC File", command=self.load_lrc_file).pack(pady=5)
        self.lrc_label = ttk.Label(self.root, text="No LRC file loaded")
        self.lrc_label.pack(pady=5)

        # Input field for the time offset
        ttk.Label(self.root, text="Enter Offset Time (format: +/-00:00.00):").pack(pady=5)
        self.offset_entry = ttk.Entry(self.root)
        self.offset_entry.pack(pady=5)
        self.offset_entry.insert(0, "00:00.00")  # Set default value
        
        # Add controls for adjusting timing
        ttk.Button(self.root, text="Adjust Timing", command=self.adjust_timing).pack(pady=5)
        self.adjustment_label = ttk.Label(self.root, text="No adjustments made")
        self.adjustment_label.pack(pady=5)

        # Add controls for saving the adjusted LRC file
        ttk.Button(self.root, text="Save Adjusted LRC", command=self.save_adjusted_lrc).pack(pady=5)

    def load_lrc_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("LRC Files", "*.lrc")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                self.lrc_lines = file.readlines()
            self.lrc_label.config(text=f"Loaded: {file_path.split('/')[-1]}")
        else:
            messagebox.showerror("Error", "No file selected.")

    def adjust_timing(self):
        if not self.lrc_lines:
            messagebox.showerror("Error", "No LRC file loaded.")
            return
    
        offset_time = self.offset_entry.get()
        if not self.validate_time_format(offset_time):
            messagebox.showerror("Error", "Invalid offset time format. Use +/-00:00.00.")
            return
    
        offset_ms = self.time_to_milliseconds(offset_time)
        adjusted_lines = []
    
        # Regex to match timestamps
        timestamp_regex = r"\[(\d+):(\d+\.\d+)\]"
    
        for line in self.lrc_lines:
            matches = re.findall(timestamp_regex, line)
            adjusted_line = line
    
            for match in matches:
                original_time = self.time_to_milliseconds(f"{match[0]}:{match[1]}")
                new_time = original_time + offset_ms
                new_time = max(new_time, 0)  # Prevent negative timestamps
                new_timestamp = self.milliseconds_to_time(new_time)
    
                # Replace the original timestamp with the adjusted timestamp
                adjusted_line = adjusted_line.replace(f"[{match[0]}:{match[1]}]", f"[{new_timestamp}]")
    
            adjusted_lines.append(adjusted_line)
    
        self.lrc_lines = adjusted_lines
        self.adjustment_label.config(text="Timing adjusted successfully!")

    def save_adjusted_lrc(self):
        if not self.lrc_lines:
            messagebox.showerror("Error", "No adjusted LRC data to save.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".lrc", filetypes=[("LRC Files", "*.lrc")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.writelines(self.lrc_lines)
            messagebox.showinfo("Saved", f"LRC saved at {file_path}")

    @staticmethod
    def validate_time_format(time_str):
        """Validate the time format is +/-00:00.00."""
        return bool(re.match(r"^-?\d{2}:\d{2}\.\d{2}$", time_str))

    @staticmethod
    def time_to_milliseconds(time_str):
        """Convert time in +/-00:00.00 format to milliseconds."""
        is_negative = time_str.startswith("-")
        time_str = time_str.lstrip("-")  # Remove the negative sign for parsing
        minutes, seconds = time_str.split(":")
        seconds, milliseconds = seconds.split(".")
        total_ms = int(minutes) * 60000 + int(seconds) * 1000 + int(milliseconds) * 10
        return -total_ms if is_negative else total_ms

    @staticmethod
    def milliseconds_to_time(milliseconds):
        """Convert milliseconds to 00:00.00 format."""
        minutes = milliseconds // 60000
        seconds = (milliseconds % 60000) // 1000
        ms = (milliseconds % 1000) // 10
        return f"{int(minutes):02}:{int(seconds):02}.{int(ms):02}"
