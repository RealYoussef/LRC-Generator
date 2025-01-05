import librosa
from tkinter import filedialog, messagebox, Tk, Text, Button
import tkinter as tk


class LRCSmartSync:
    def __init__(self, root, setup_menu_callback):
        self.root = root
        self.setup_menu_callback = setup_menu_callback
        self.audio_path = ""
        self.lyrics = []
        self.setup_ui()

    def setup_ui(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Setup menu
        self.setup_menu_callback()
        
        # Instruction label
        tk.Label(self.root, text="LRC Time Sync Tool", font=("Helvetica", 16, "bold")).pack(pady=10)

        # Title
        Button(self.root, text="Load Audio File", command=self.load_audio).pack(pady=10)
        Button(self.root, text="Load LRC File", command=self.load_lrc).pack(pady=10)
        self.lrc_text = Text(self.root, width=80, height=20)
        self.lrc_text.pack(pady=10)
        Button(self.root, text="Sync Timings", command=self.sync_timings).pack(pady=10)
        Button(self.root, text="Save LRC File", command=self.save_lrc).pack(pady=10)

    def load_audio(self):
        self.audio_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.m4a")])
        if not self.audio_path:
            messagebox.showerror("Error", "No audio file selected.")
        else:
            messagebox.showinfo("Audio Loaded", f"Loaded: {self.audio_path}")

    def load_lrc(self):
        lrc_path = filedialog.askopenfilename(filetypes=[("LRC Files", "*.lrc")])
        if not lrc_path:
            messagebox.showerror("Error", "No LRC file selected.")
            return

        try:
            with open(lrc_path, "r", encoding="utf-8") as file:
                self.lyrics = file.readlines()
                self.lrc_text.delete(1.0, "end")
                self.lrc_text.insert("end", "".join(self.lyrics))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load LRC file: {e}")

    def sync_timings(self):
        if not self.audio_path or not self.lyrics:
            messagebox.showerror("Error", "Load both audio and LRC files first.")
            return
    
        try:
            # Load audio and detect beats
            y, sr = librosa.load(self.audio_path)
            _, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
            synced_lyrics = []
            current_beat_index = 0
            adjusted_timings = []
    
            # Extract and process original timings
            original_timings = []
            lyrics_text = []
            line_mapping = []  # Keeps track of which lines contain timestamps
    
            for line in self.lyrics:
                if line.startswith("[") and "]" in line:
                    try:
                        # Extract timestamp and lyrics
                        timestamp, text = line.split("]", 1)
                        minutes, seconds = map(float, timestamp[1:].split(":"))
                        original_time = minutes * 60 + seconds
                        original_timings.append(original_time)
                        lyrics_text.append(text.strip())
                        line_mapping.append(True)  # Line has a timestamp
                    except Exception:
                        synced_lyrics.append(line)  # Keep non-timestamp lines as-is
                        line_mapping.append(False)  # Line does not have a timestamp
                else:
                    synced_lyrics.append(line)
                    line_mapping.append(False)
    
            # Dynamic adjustment of timings
            for i, original_time in enumerate(original_timings):
                # Find the nearest beat
                while current_beat_index < len(beat_times) - 1 and beat_times[current_beat_index] < original_time:
                    current_beat_index += 1
    
                # Align to nearest beat but ensure natural gaps
                if i == 0:
                    adjusted_time = beat_times[current_beat_index]
                else:
                    prev_time = adjusted_timings[-1]
                    gap = original_timings[i] - original_timings[i - 1]
    
                    # Adjust the gap based on original timing and beats
                    adjusted_time = max(
                        prev_time + max(0.5, gap),  # Maintain a minimum gap of 0.5 seconds
                        beat_times[current_beat_index - 1] if current_beat_index > 0 else beat_times[0]
                    )
    
                # Ensure the adjusted time does not overlap with the next line
                if i < len(original_timings) - 1:
                    next_time = original_timings[i + 1]
                    adjusted_time = min(adjusted_time, next_time - 0.5)  # Keep at least 0.5s before next line
    
                adjusted_timings.append(adjusted_time)
    
            # Rebuild the synced lyrics while preserving non-timed lines
            synced_lyrics = []
            timing_index = 0
    
            for has_timing, line in zip(line_mapping, self.lyrics):
                if has_timing:
                    adjusted_time = adjusted_timings[timing_index]
                    new_minutes = int(adjusted_time // 60)
                    new_seconds = adjusted_time % 60
                    new_timestamp = f"[{new_minutes:02}:{new_seconds:05.2f}]"
                    synced_lyrics.append(f"{new_timestamp}{lyrics_text[timing_index]}")
                    timing_index += 1
                else:
                    synced_lyrics.append(line.strip())  # Preserve non-timed lines exactly
    
            # Update the LRC text box
            self.lrc_text.delete(1.0, "end")
            self.lrc_text.insert("end", "\n".join(synced_lyrics))
            messagebox.showinfo("Success", "Timings have been dynamically synchronized.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to synchronize timings: {e}")


    def save_lrc(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".lrc", filetypes=[("LRC Files", "*.lrc")])
        if not save_path:
            return

        try:
            with open(save_path, "w", encoding="utf-8") as file:
                file.write(self.lrc_text.get("1.0", "end"))
            messagebox.showinfo("Success", f"LRC file saved at {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save LRC file: {e}")


if __name__ == "__main__":
    root = Tk()
    app = LRCSmartSync(root, lambda: None)
    root.mainloop()
