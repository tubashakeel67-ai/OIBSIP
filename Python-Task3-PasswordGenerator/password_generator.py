"""
password_generator.py — tkinter GUI for the Random Password Generator.

Handles presentation and user interaction only. All actual logic
(validation, generation, strength scoring) lives in core.py and is
imported here.
"""

import tkinter as tk
from tkinter import messagebox
import pyperclip
from core import validate_input, generate_password, check_strength

root = tk.Tk()
root.title("Password Generator")
root.geometry("400x640")
root.resizable(False, False)
root.configure(bg="#1a1d29")

# ---------- Style constants ----------
FONT = ("Segoe UI", 9)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_HEADER = ("Segoe UI", 15, "bold")
MONO_FONT = ("Consolas", 13)
MONO_SMALL = ("Consolas", 9)

BG = "#1a1d29"
CARD_BG = "#242837"
ACCENT = "#7c5cff"
ACCENT_DARK = "#6a4de8"
TEXT_LIGHT = "#e8e9ed"
TEXT_MUTED = "#8b8fa3"
FIELD_BG = "#1e222e"

# In-memory session history: holds up to the last 5 generated passwords.
# Newest is always at index 0. Cleared automatically when the app closes
# (never written to disk), per the brief's "session-only" requirement.
history = []

# ---------- Header ----------
header_frame = tk.Frame(root, bg=BG, pady=16)
header_frame.pack(fill="x")
tk.Label(header_frame, text="🔐 Password Generator", font=FONT_HEADER, bg=BG, fg=TEXT_LIGHT).pack()
tk.Label(header_frame, text="Secure • Customizable • Instant", font=("Segoe UI", 8), bg=BG, fg=TEXT_MUTED).pack(pady=(2, 0))

# ---------- Options card: length slider + character type checkboxes ----------
options_frame = tk.Frame(root, bg=CARD_BG, padx=16, pady=12)
options_frame.pack(fill="x", padx=15, pady=(4, 8))

tk.Label(options_frame, text="LENGTH", font=("Segoe UI", 8, "bold"), bg=CARD_BG, fg=ACCENT).pack(anchor="w")

length_var = tk.IntVar(value=12)
length_row = tk.Frame(options_frame, bg=CARD_BG)
length_row.pack(fill="x", pady=(2, 10))
length_slider = tk.Scale(length_row, from_=8, to=32, orient="horizontal", variable=length_var,
                          bg=CARD_BG, font=FONT, highlightthickness=0, troughcolor=FIELD_BG,
                          activebackground=ACCENT, fg=TEXT_LIGHT, showvalue=True,
                          sliderlength=14, bd=0)
length_slider.pack(fill="x")

tk.Label(options_frame, text="CHARACTER TYPES", font=("Segoe UI", 8, "bold"), bg=CARD_BG, fg=ACCENT).pack(anchor="w", pady=(0, 4))

# Shared style dict for all 5 checkboxes below
check_style = dict(font=FONT, bg=CARD_BG, fg=TEXT_LIGHT, anchor="w", activebackground=CARD_BG,
                    selectcolor=FIELD_BG, highlightthickness=0, bd=0)

# Each checkbox is bound to its own BooleanVar. These are read fresh
# (via .get()) only when Generate is clicked — not cached earlier —
# so they always reflect the user's current choices.
use_upper_var = tk.BooleanVar(value=True)
tk.Checkbutton(options_frame, text="Uppercase (A-Z)", variable=use_upper_var, **check_style).pack(fill="x")

use_lower_var = tk.BooleanVar(value=True)
tk.Checkbutton(options_frame, text="Lowercase (a-z)", variable=use_lower_var, **check_style).pack(fill="x")

use_digits_var = tk.BooleanVar(value=True)
tk.Checkbutton(options_frame, text="Numbers (0-9)", variable=use_digits_var, **check_style).pack(fill="x")

use_symbols_var = tk.BooleanVar(value=True)
tk.Checkbutton(options_frame, text="Symbols ( . _ @ # $ % & * )", variable=use_symbols_var, **check_style).pack(fill="x")

exclude_ambiguous_var = tk.BooleanVar(value=False)
tk.Checkbutton(options_frame, text="Exclude Ambiguous (0, O, l, 1)", variable=exclude_ambiguous_var, **check_style).pack(fill="x")

# ---------- Result card: generated password, strength, copy button ----------
result_frame = tk.Frame(root, bg=CARD_BG, padx=16, pady=12)
result_frame.pack(fill="x", padx=15, pady=6)

# Read-only Entry: displays the password but blocks manual typing/editing,
# so what's shown always matches exactly what generate_password() produced.
password_display = tk.Entry(result_frame, font=MONO_FONT, justify="center", state="readonly",
                             relief="flat", bg=FIELD_BG, fg=ACCENT, readonlybackground=FIELD_BG,
                             insertbackground=TEXT_LIGHT)
password_display.pack(fill="x", ipady=8)

# Bound to a StringVar so the label text can be updated live via .set()
# without needing to recreate the widget on every generation.
strength_var = tk.StringVar(value="")
strength_label = tk.Label(result_frame, textvariable=strength_var, font=FONT_BOLD, bg=CARD_BG, fg=TEXT_MUTED)
strength_label.pack(pady=(8, 8))


def on_copy_click():
    """Manually re-copies whatever password is currently displayed."""
    current_password = password_display.get()
    if current_password:
        pyperclip.copy(current_password)


copy_button = tk.Button(result_frame, text="📋  Copy to Clipboard", font=FONT, command=on_copy_click,
                         bg=FIELD_BG, fg=TEXT_LIGHT, relief="flat", cursor="hand2", pady=6,
                         activebackground="#2a2f40", activeforeground=TEXT_LIGHT)
copy_button.pack(fill="x")


def on_generate_click():
    """
    Main Generate button handler:
      1. Reads current values from all tkinter variables.
      2. Validates them via core.validate_input().
         - If invalid: shows an error popup and clears the display/strength.
      3. If valid: generates a password, scores its strength, displays
         both, copies the password to the clipboard automatically, and
         updates the session history (keeping only the last 5).
    """
    length = length_var.get()
    use_upper = use_upper_var.get()
    use_lower = use_lower_var.get()
    use_digits = use_digits_var.get()
    use_symbols = use_symbols_var.get()
    exclude_ambiguous = exclude_ambiguous_var.get()

    error = validate_input(length, use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous)

    if error is not None:
        messagebox.showerror("Invalid Input", error)
        # Clear any stale password/strength from a previous successful
        # generation, so nothing misleading is left on screen.
        strength_var.set("")
        password_display.config(state="normal")
        password_display.delete(0, tk.END)
        password_display.config(state="readonly")
        return

    password = generate_password(length, use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous)
    strength = check_strength(length, use_upper, use_lower, use_digits, use_symbols)

    # Briefly unlock the read-only Entry to update its text, then lock it again.
    password_display.config(state="normal")
    password_display.delete(0, tk.END)
    password_display.insert(0, password)
    password_display.config(state="readonly")

    # Color-code the strength label for an at-a-glance read.
    strength_colors = {"Weak": "#ff5c7a", "Medium": "#ffb84d", "Strong": "#4ade9a"}
    strength_label.config(fg=strength_colors.get(strength, TEXT_MUTED))
    strength_var.set(f"● Strength: {strength}")

    pyperclip.copy(password)

    # Update session history: newest at index 0, capped at 5 entries.
    global history
    history.insert(0, password)
    history = history[:5]
    refresh_history_display()


generate_button = tk.Button(root, text="⚡ Generate Password", font=FONT_BOLD, bg=ACCENT, fg="white",
                             activebackground=ACCENT_DARK, activeforeground="white",
                             relief="flat", pady=9, cursor="hand2", command=on_generate_click)
generate_button.pack(fill="x", padx=15, pady=(0, 8))

# ---------- History card: last 5 generated passwords (session only) ----------
history_card = tk.Frame(root, bg=CARD_BG, padx=16, pady=10)
history_card.pack(fill="both", expand=True, padx=15, pady=(0, 15))

history_header = tk.Frame(history_card, bg=CARD_BG)
history_header.pack(fill="x", pady=(0, 6))

tk.Label(history_header, text="🕘 RECENT PASSWORDS", font=("Segoe UI", 8, "bold"), bg=CARD_BG, fg=ACCENT).pack(side="left")
tk.Label(history_header, text="session only", font=("Segoe UI", 7), bg=CARD_BG, fg=TEXT_MUTED).pack(side="left", padx=(6, 0))

history_listbox = tk.Listbox(history_card, font=MONO_SMALL, height=5, bd=0, relief="flat",
                              bg=FIELD_BG, fg=TEXT_LIGHT, selectbackground=ACCENT, selectforeground="white",
                              highlightthickness=0, activestyle="none")
history_listbox.pack(fill="both", expand=True)


def refresh_history_display():
    """Redraws the history Listbox from the current `history` list."""
    history_listbox.delete(0, tk.END)
    for item in history:
        history_listbox.insert(tk.END, item)


root.mainloop()