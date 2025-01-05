import warnings
import re
import pykakasi
from tkinter import ttk, filedialog, messagebox, scrolledtext
import tkinter as tk

warnings.filterwarnings("ignore", category=DeprecationWarning)


class RomajiConverter:
    def __init__(self, root, setup_menu_callback):
        self.root = root
        self.root.title("Romaji Converter")
        self.root.geometry("800x900")

        # Setup the shared menu
        self.setup_menu_callback = setup_menu_callback
        self.setup_menu_callback()

        # Default font size
        self.text_font_size = 12

        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self.root, text="Romaji Converter", font=("Helvetica", 18)).pack(pady=10)

        # Text box for input lyrics
        ttk.Label(self.root, text="Input Japanese Lyrics:").pack(pady=5)
        self.input_text = scrolledtext.ScrolledText(
            self.root, width=70, height=10, font=("Helvetica", self.text_font_size)
        )
        self.input_text.pack(pady=5)
        self.add_context_menu_and_shortcuts(self.input_text)  # Add right-click menu and Ctrl+A shortcut

        # Convert button
        ttk.Button(self.root, text="Convert to Romaji", command=self.convert_to_romaji).pack(pady=5)

        # Text box for output lyrics
        ttk.Label(self.root, text="Converted Romaji Lyrics:").pack(pady=5)
        self.output_text = scrolledtext.ScrolledText(
            self.root, width=70, height=10, state="normal", font=("Helvetica", self.text_font_size)
        )
        self.output_text.pack(pady=5)
        self.add_context_menu_and_shortcuts(self.output_text)  # Add right-click menu and Ctrl+A shortcut
        self.output_text.config(state="disabled")

        # Font adjustment buttons
        font_adjust_frame = ttk.Frame(self.root)
        font_adjust_frame.pack(pady=5)

        ttk.Button(
            font_adjust_frame, text="Increase Font Size", command=self.increase_font_size
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            font_adjust_frame, text="Decrease Font Size", command=self.decrease_font_size
        ).pack(side=tk.LEFT, padx=5)

    def add_context_menu_and_shortcuts(self, text_widget):
        """Add a right-click menu and Ctrl+A shortcut for a text widget."""
        # Context menu
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Copy", command=lambda: self.copy_text(text_widget))
        context_menu.add_command(label="Paste", command=lambda: self.paste_text(text_widget))
        context_menu.add_command(label="Select All", command=lambda: self.select_all_text(text_widget))

        # Bind right-click to show the context menu
        text_widget.bind("<Button-3>", lambda event: self.show_context_menu(event, context_menu))

        # Bind Ctrl+A for "Select All"
        text_widget.bind("<Control-a>", lambda event: self.select_all_text(text_widget))
        text_widget.bind("<Control-A>", lambda event: self.select_all_text(text_widget))  # For uppercase 'A'

    def show_context_menu(self, event, menu):
        """Display the context menu at the mouse position."""
        menu.tk_popup(event.x_root, event.y_root)

    def copy_text(self, text_widget):
        """Copy the selected text to the clipboard."""
        try:
            selected_text = text_widget.selection_get()
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            self.root.update()
        except tk.TclError:
            messagebox.showerror("Error", "No text selected to copy.")

    def paste_text(self, text_widget):
        """Paste text from the clipboard into the text widget."""
        try:
            clipboard_text = self.root.clipboard_get()
            text_widget.insert(tk.INSERT, clipboard_text)
        except tk.TclError:
            messagebox.showerror("Error", "Clipboard is empty.")

    def select_all_text(self, text_widget):
        """Select all text in the text widget."""
        text_widget.tag_add("sel", "1.0", tk.END)
        text_widget.mark_set(tk.INSERT, "1.0")
        text_widget.see(tk.INSERT)

    def increase_font_size(self):
        """Increase the font size of the text boxes."""
        self.text_font_size += 2
        self.input_text.config(font=("Helvetica", self.text_font_size))
        self.output_text.config(font=("Helvetica", self.text_font_size))

    def decrease_font_size(self):
        """Decrease the font size of the text boxes."""
        if self.text_font_size > 8:  # Prevent font size from becoming too small
            self.text_font_size -= 2
            self.input_text.config(font=("Helvetica", self.text_font_size))
            self.output_text.config(font=("Helvetica", self.text_font_size))

    def convert_to_romaji(self):
        # Get input text
        input_text = self.input_text.get("1.0", tk.END).strip()

        if not input_text:
            messagebox.showerror("Error", "Please enter lyrics to convert.")
            return

        # Perform conversion
        try:
            converted_text = self.convert_to_romaji_with_contextual_replacements(input_text)
            self.output_text.config(state="normal")
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", converted_text)
            self.output_text.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed: {e}")

    @staticmethod
    def convert_to_romaji_with_contextual_replacements(text):
        kakasi = pykakasi.kakasi()
        kakasi.setMode("H", "a")  # Hiragana to ascii
        kakasi.setMode("K", "a")  # Katakana to ascii
        kakasi.setMode("J", "a")  # Japanese to ascii
        kakasi.setMode("r", "Hepburn")  # Use Hepburn Romanization
        kakasi.setMode("s", True)  # Enable word segmentation
        converter = kakasi.getConverter()

        lines = text.splitlines()
        romaji_lines = []

        for line in lines:
            words = line.split()
            converted_line = []
            for word in words:
                converted_word = converter.do(word)
                converted_line.append(converted_word)

            romaji_line = " ".join(converted_line)

            # Apply replacement rules
            romaji_line = re.sub(r'\bha\b', 'wa', romaji_line)
            romaji_line = re.sub(r'(?<!\S)ha(?!\S)', 'wa', romaji_line)
            romaji_line = re.sub(r'(?<=\w)ha(?=\s|$)', lambda m: m.group(0).replace('ha', 'wa'), romaji_line)
            romaji_line = re.sub(r'\bashita\b', 'asu', romaji_line)
            romaji_line = re.sub(r'\bkun\b', 'kimi', romaji_line)

            # Replace punctuation with a consistent format
            romaji_line = romaji_line.replace("。", ".")

            romaji_lines.append(romaji_line)

        return "\n".join(romaji_lines)
