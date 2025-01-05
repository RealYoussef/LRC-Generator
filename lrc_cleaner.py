import re
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class LRCCleaner:
    def __init__(self, root, setup_menu_callback):
        self.root = root
        self.root.title("LRC Cleaner")
        self.root.geometry("800x900")

        # Setup the shared menu
        self.setup_menu_callback = setup_menu_callback
        self.setup_menu_callback()

        # Default font size
        self.text_font_size = 12

        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self.root, text="LRC Cleaner", font=("Helvetica", 18)).pack(pady=10)

        # Input text box
        ttk.Label(self.root, text="Input LRC Lyrics:").pack(pady=5)
        self.input_text = scrolledtext.ScrolledText(
            self.root, width=70, height=10, font=("Helvetica", self.text_font_size)
        )
        self.input_text.pack(pady=5)
        self.add_context_menu_and_shortcuts(self.input_text)

        # Process button
        ttk.Button(self.root, text="Remove LRC Format", command=self.process_lrc).pack(pady=5)

        # Output text box
        ttk.Label(self.root, text="Plain Lyrics:").pack(pady=5)
        self.output_text = scrolledtext.ScrolledText(
            self.root, width=70, height=10, state="normal", font=("Helvetica", self.text_font_size)
        )
        self.output_text.pack(pady=5)
        self.add_context_menu_and_shortcuts(self.output_text)
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

    def process_lrc(self):
        """Remove LRC formatting and display plain lyrics."""
        lrc_text = self.input_text.get("1.0", tk.END).strip()

        if not lrc_text:
            messagebox.showerror("Error", "Please enter LRC text to process.")
            return

        # Process the LRC text
        plain_lyrics = self.remove_lrc_format(lrc_text)

        # Display the output
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", plain_lyrics)
        self.output_text.config(state="disabled")

    @staticmethod
    def remove_lrc_format(lrc_text):
        """Removes LRC tags and timestamps while preserving line breaks."""
        lines = lrc_text.splitlines()
        cleaned_lines = []
        for line in lines:
            # Remove LRC metadata tags (e.g., [ti:...], [ar:...], [al:...])
            if re.match(r"^\[.*?:.*?\]$", line.strip()):
                continue
            # Remove timestamp tags (e.g., [00:11.65])
            cleaned_line = re.sub(r"\[.*?\]", "", line).strip()
            # Add the line if it's not empty, preserving blank lines
            cleaned_lines.append(cleaned_line if cleaned_line else "")
        return "\n".join(cleaned_lines)

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
        text_widget.bind("<Control-A>", lambda event: self.select_all_text(text_widget))

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
