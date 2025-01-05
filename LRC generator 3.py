import tkinter as tk
from tkinter import filedialog, messagebox
from mutagen import File
import pygame
import time
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from mutagen.id3 import ID3, TIT2, TPE1, TALB
import ffmpeg
import os
import ttkbootstrap as ttk
from threading import Thread
import subprocess
import sys

# Get the directory of the current script
BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

# Update file paths
logo_path = os.path.join(BASE_DIR, "Logo5.png")
icon_path = os.path.join(BASE_DIR, "Logo5.ico")

# def show_splash():
#     # Path to the splash screen script
#     splash_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "splash_screen.py")
#     subprocess.run(["python", splash_script])

class LRCGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("LRC Application")
        self.root.geometry("800x900")
        self.style = ttk.Style(theme="darkly")  # Use solar-themed material design
        
        # Set the window icon
        self.root.iconbitmap(icon_path)

        # Initialize pygame mixer
        pygame.mixer.init()

        # Variables
        self.audio_path = ""
        self.metadata = {"title": "Unknown", "artist": "Unknown", "album": "Unknown"}
        self.lyrics = []
        self.original_lyrics = []  # Store the original unsynchronized lyrics
        self.current_line = 0
        self.start_time = 0
        self.playing = False

        # Text box font size variable
        self.text_font_size = 12

        # Bind the close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # UI Elements
        self.load_lrc_generator()
        
    def setup_menu(self):
        """Setup a custom Menubutton for the hamburger menu."""
        menu_bar = tk.Menu(self.root)
    
        # Programs menu
        programs_menu = tk.Menu(menu_bar, tearoff=0)
        programs_menu.add_command(label="LRC Generator", command=self.load_lrc_generator)
        programs_menu.add_command(label="LRC Timing Adjuster", command=self.load_lrc_timing_adjuster)
        programs_menu.add_command(label="LRC Remover", command=self.load_lrc_cleaner)
        programs_menu.add_command(label="Romaji Converter", command=self.load_romaji_converter)
        programs_menu.add_command(label="LRC Time Sync", command=self.load_lrc_time_sync)
        programs_menu.add_command(label="LRC Smart Sync", command=self.load_lrc_smart_sync)
        programs_menu.add_separator()
        programs_menu.add_command(label="Exit", command=self.on_close)
    
        menu_bar.add_cascade(label="Programs", menu=programs_menu)
    
        # Attach the menu bar to the root window
        self.root.config(menu=menu_bar)

    def load_lrc_timing_adjuster(self):
        """Load the LRC Timing Adjuster interface."""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
    
        # Import and initialize the LRC Timing Adjuster with the shared menu
        try:
            from lrc_timing_adjuster import LRCTimingAdjuster
            LRCTimingAdjuster(self.root, self.setup_menu)
        except ImportError as e:
            messagebox.showerror("Error", f"Failed to load LRC Timing Adjuster: {e}")

    def setup_ui(self):
        # Create a top frame for the menu and "Select Audio File" button
        top_frame = ttk.Frame(self.root)
        top_frame.pack(side="top", fill="x", pady=5)
    
        # Use grid in the top frame for precise alignment
        top_frame.grid_columnconfigure(0, weight=1)  # Left spacer
        top_frame.grid_columnconfigure(1, weight=0)  # Menu
        top_frame.grid_columnconfigure(2, weight=1)  # Center spacer
        top_frame.grid_columnconfigure(3, weight=0)  # Button
        top_frame.grid_columnconfigure(4, weight=1)  # Right spacer
    
        # Add the hamburger menu in the left column
        menu_frame = ttk.Frame(top_frame)
        menu_frame.grid(row=0, column=0, sticky="w", padx=5)
        self.setup_menu()
    
        # Add the "Select Audio File" button in the center
        select_button = ttk.Button(
            top_frame,
            text="Select Audio File",
            command=self.select_audio,
            bootstyle="success-outline"
        )
        select_button.grid(row=0, column=2, padx=5)

        # Add the audio file label
        self.audio_label = ttk.Label(self.root, text="No audio file selected", bootstyle="info")
        self.audio_label.pack(pady=5)

        # Lyrics text input
        ttk.Label(self.root, text="Enter Lyrics (one line per stanza):", bootstyle="info").pack(pady=5)
        self.lyrics_text = tk.Text(
            self.root, 
            width=60, 
            height=15, 
            bg="#FFF8E1", 
            fg="#795548", 
            insertbackground="#795548", 
            font=("Helvetica", self.text_font_size)
        )
        self.lyrics_text.pack(pady=5)

        # Buttons in a horizontal frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Load Metadata", command=self.load_metadata, bootstyle="primary-outline").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Play Audio", command=self.play_pause_audio, bootstyle="success-outline").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Stop Audio", command=self.stop_audio, bootstyle="danger-outline").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Add Timestamp", command=self.add_timestamp, bootstyle="warning-outline").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset Timestamps", command=self.reset_timestamps, bootstyle="secondary-outline").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset_preview, bootstyle="secondary-outline").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save LRC", command=self.save_lrc, bootstyle="info-outline").pack(side=tk.LEFT, padx=5)

        # Font scaling buttons
        font_button_frame = ttk.Frame(self.root)
        font_button_frame.pack(pady=10)

        ttk.Button(font_button_frame, text="Increase Font Size", command=self.increase_font_size, bootstyle="success-outline").pack(side=tk.LEFT, padx=5)
        ttk.Button(font_button_frame, text="Decrease Font Size", command=self.decrease_font_size, bootstyle="danger-outline").pack(side=tk.LEFT, padx=5)

        # Preview area
        ttk.Label(self.root, text="Preview LRC:", bootstyle="info").pack(pady=5)
        self.preview_text = tk.Text(
            self.root, 
            width=60, 
            height=15, 
            bg="#FFF8E1", 
            fg="#795548", 
            state="disabled", 
            font=("Helvetica", self.text_font_size)
        )
        self.preview_text.pack(pady=5)
        
    def load_lrc_generator(self):
        """Load the LRC Generator interface."""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
    
        # Reload the UI elements
        self.setup_ui()

    def load_lrc_cleaner(self):
        """Load the LRC Cleaner interface."""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
    
        # Import and initialize the LRC Cleaner
        try:
            from lrc_cleaner import LRCCleaner
            LRCCleaner(self.root, self.setup_menu)
        except ImportError as e:
            messagebox.showerror("Error", f"Failed to load LRC Cleaner: {e}")

    def load_romaji_converter(self):
        """Load the Romaji Converter interface."""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
    
        # Import and initialize the Romaji Converter
        try:
            from romaji_converter import RomajiConverter
            RomajiConverter(self.root, self.setup_menu)
        except ImportError as e:
            messagebox.showerror("Error", f"Failed to load Romaji Converter: {e}")
            
    def load_lrc_time_sync(self):
        """Load the LRC Time Sync interface."""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
    
        # Import and initialize the LRC Time Sync tool
        try:
            from lrc_time_sync import LRCTimeSync
            LRCTimeSync(self.root, self.setup_menu)
        except ImportError as e:
            messagebox.showerror("Error", f"Failed to load LRC Time Sync: {e}")
            
    def load_lrc_smart_sync(self):
        """Load the LRC Smart Sync interface."""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
    
        # Import and initialize the LRC Smart Sync tool
        try:
            from lrc_smart_sync import LRCSmartSync
            LRCSmartSync(self.root, self.setup_menu)
        except ImportError as e:
            messagebox.showerror("Error", f"Failed to load LRC Smart Sync: {e}")
            
    def select_audio(self):
        self.audio_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.flac *.m4a")])
        if self.audio_path:
            self.audio_label.config(text=f"Selected: {self.audio_path.split('/')[-1]}")
            self.load_metadata()
        else:
            messagebox.showerror("Error", "No audio file selected.")
            
    def load_metadata(self):
        if not self.audio_path:
            messagebox.showerror("Error", "No audio file selected.")
            return
    
        try:
            audio_metadata = None
    
            if self.audio_path.endswith(".mp3"):
                audio = MP3(self.audio_path, ID3=ID3)
                title = audio.tags.get("TIT2", None)
                artist = audio.tags.get("TPE1", None)
                album = audio.tags.get("TALB", None)
                self.metadata = {
                    "title": title.text[0] if title else "Unknown",
                    "artist": artist.text[0] if artist else "Unknown",
                    "album": album.text[0] if album else "Unknown",
                }
    
            elif self.audio_path.endswith(".m4a"):
                audio = MP4(self.audio_path)
                self.metadata = {
                    "title": audio.tags.get("\xa9nam", ["Unknown"])[0],
                    "artist": audio.tags.get("\xa9ART", ["Unknown"])[0],
                    "album": audio.tags.get("\xa9alb", ["Unknown"])[0],
                }
    
            elif self.audio_path.endswith(".flac"):
                audio = FLAC(self.audio_path)
                self.metadata = {
                    "title": audio.get("title", ["Unknown"])[0],
                    "artist": audio.get("artist", ["Unknown"])[0],
                    "album": audio.get("album", ["Unknown"])[0],
                }
    
            else:
                self.metadata = {
                    "title": "Unknown",
                    "artist": "Unknown",
                    "album": "Unknown",
                }
    
            messagebox.showinfo(
                "Metadata Loaded",
                f"Title: {self.metadata['title']}\n"
                f"Artist: {self.metadata['artist']}\n"
                f"Album: {self.metadata['album']}",
            )
    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load metadata: {e}")

    def play_pause_audio(self):
        if not self.audio_path:
            messagebox.showerror("Error", "No audio file selected.")
            return
    
        # Check if the file is an .m4a file
        if self.audio_path.endswith(".m4a"):
            # Convert .m4a to .wav using ffmpeg
            wav_path = self.audio_path.rsplit(".", 1)[0] + "_converted.wav"
            try:
                # If the converted file already exists, reuse it
                if not os.path.exists(wav_path):
                    ffmpeg.input(self.audio_path).output(wav_path).run(overwrite_output=True)
                self.audio_path = wav_path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to convert .m4a file: {e}")
                return
    
        # Load and play the audio file
        try:
            pygame.mixer.music.load(self.audio_path)
            pygame.mixer.music.play()
            self.start_time = time.time()
            self.playing = True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play audio: {e}")
            
    def stop_audio(self):
        # Stop the audio playback
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.playing = False  # Update the playing state
            
    def reset_preview(self):
        """Clear the preview LRC text box and reset original lyrics."""
        self.preview_text.config(state="normal")
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.config(state="disabled")
        
        # Reset the original lyrics and related variables
        self.original_lyrics = []
        self.lyrics = []
        self.current_line = 0
        self.start_time = 0
        
        # Clear the lyrics input text box
        self.lyrics_text.delete(1.0, tk.END)
        
        messagebox.showinfo("Reset", "Preview LRC and lyrics have been cleared.")

    def add_timestamp(self):
        if not self.lyrics:
            self.original_lyrics = self.lyrics_text.get("1.0", tk.END).strip().split("\n")
            self.lyrics = self.original_lyrics.copy()
    
        # Skip over empty lines
        while self.current_line < len(self.lyrics) and not self.lyrics[self.current_line].strip():
            self.current_line += 1
    
        if self.current_line >= len(self.lyrics):
            messagebox.showinfo("Completed", "All lines have been synchronized.")
            return
    
        elapsed_time = time.time() - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        milliseconds = int((elapsed_time - int(elapsed_time)) * 100)
        timestamp = f"[{minutes:02}:{seconds:02}.{milliseconds:02}]"
    
        # Add timestamp to the current line
        self.lyrics[self.current_line] = f"{timestamp}{self.lyrics[self.current_line]}"
        self.update_preview()
    
        # Highlight the next line in original lyrics
        self.lyrics_text.tag_remove("highlight", "1.0", tk.END)  # Remove previous highlights
        if self.current_line + 1 < len(self.lyrics):
            self.lyrics_text.tag_add("highlight", f"{self.current_line + 2}.0", f"{self.current_line + 2}.end")
            self.lyrics_text.tag_configure("highlight", underline=True)
    
        # Highlight the next line in preview text
        self.preview_text.tag_remove("highlight", "1.0", tk.END)  # Remove previous highlights
        if self.current_line + 1 < len(self.lyrics):
            self.preview_text.tag_add("highlight", f"{self.current_line + 2}.0", f"{self.current_line + 2}.end")
            self.preview_text.tag_configure("highlight", underline=True)
    
        # Auto-scroll original lyrics and preview text to show the current line and the next 5 lines
        self.lyrics_text.see(f"{self.current_line + 1}.0")  # Scroll to the current line
        for i in range(1, 6):  # Scroll to ensure the next 5 lines are visible
            if self.current_line + i < len(self.lyrics):
                self.lyrics_text.see(f"{self.current_line + i + 1}.0")
    
        self.preview_text.see(f"{self.current_line + 1}.0")
        for i in range(1, 6):  # Scroll to ensure the next 5 lines in preview
            if self.current_line + i < len(self.lyrics):
                self.preview_text.see(f"{self.current_line + i + 1}.0")
    
        # Move to the next line
        self.current_line += 1
    
        # Skip over empty lines again
        while self.current_line < len(self.lyrics) and not self.lyrics[self.current_line].strip():
            self.current_line += 1

    def reset_timestamps(self):
        if not self.original_lyrics:
            messagebox.showinfo("Info", "No lyrics to reset.")
            return

        # Reset lyrics and synchronization state
        self.lyrics = self.original_lyrics.copy()
        self.current_line = 0
        self.update_preview()
        messagebox.showinfo("Reset", "Timestamps have been reset.")

    def save_lrc(self):
        if not self.lyrics:
            messagebox.showerror("Error", "No lyrics entered.")
            return
    
        # Get the audio file's base name without extension
        if self.audio_path:
            base_name = self.audio_path.split("/")[-1]
            if base_name.endswith("_converted.wav"):
                base_name = base_name.replace("_converted.wav", "")  # Remove "_converted.wav"
            else:
                base_name = base_name.rsplit(".", 1)[0]  # Remove the original file extension
            default_filename = base_name + ".lrc"
        else:
            default_filename = "output.lrc"
    
        # Open save dialog with default filename
        file_path = filedialog.asksaveasfilename(
            defaultextension=".lrc",
            initialfile=default_filename,
            filetypes=[("LRC Files", "*.lrc")]
        )
        if not file_path:
            return
    
        # Write LRC file
        with open(file_path, "w", encoding="utf-8") as lrc_file:
            lrc_file.write(f"[ti:{self.metadata['title']}]\n")
            lrc_file.write(f"[ar:{self.metadata['artist']}]\n")
            lrc_file.write(f"[al:{self.metadata['album']}]\n")
            lrc_file.write("\n".join(self.lyrics))
    
        messagebox.showinfo("Saved", f"LRC file saved at {file_path}")

    def increase_font_size(self):
        """Increase the font size of the text boxes."""
        self.text_font_size += 2
        self.lyrics_text.config(font=("Helvetica", self.text_font_size))
        self.preview_text.config(font=("Helvetica", self.text_font_size))

    def decrease_font_size(self):
        """Decrease the font size of the text boxes."""
        if self.text_font_size > 8:  # Prevent font size from becoming too small
            self.text_font_size -= 2
            self.lyrics_text.config(font=("Helvetica", self.text_font_size))
            self.preview_text.config(font=("Helvetica", self.text_font_size))

    def update_preview(self):
        self.preview_text.config(state="normal")
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, "\n".join(self.lyrics))
        self.preview_text.config(state="disabled")

    def on_close(self):
        # Stop audio playback
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        # Quit the pygame mixer
        pygame.mixer.quit()

        # Delete the converted WAV file if it exists
        if hasattr(self, 'audio_path') and self.audio_path.endswith("_converted.wav"):
            try:
                os.remove(self.audio_path)
                print(f"Deleted temporary WAV file: {self.audio_path}")
            except Exception as e:
                print(f"Failed to delete temporary WAV file: {e}")

        # Close the application
        self.root.destroy()

def main():
    # Start the splash screen in a separate thread
    # splash_thread = Thread(target=show_splash)
    # splash_thread.start()

    # Load the tkinter application
    root = ttk.Window(themename="solar")
    app = LRCGenerator(root)
    root.mainloop()

    # Wait for the splash thread to finish
    # splash_thread.join()
if __name__ == "__main__":
    main()