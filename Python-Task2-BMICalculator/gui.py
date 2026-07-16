"""
gui.py
tkinter GUI layer — imports logic from bmi_logic.py, database.py, and chart.py
"""
import tkinter as tk
from bmi_logic import validate_input, calculate_bmi, classify_bmi
from database import init_db, save_record
from chart import show_bmi_trend

init_db()


def get_validated_bmi(weight_str, height_str):
    is_valid, weight, height = validate_input(weight_str, height_str)
    if not is_valid:
        return False, None, None, None, None
    bmi = calculate_bmi(weight, height)
    category = classify_bmi(bmi)
    return True, weight, height, bmi, category


def on_calculate():
    result = get_validated_bmi(weight_entry.get(), height_entry.get())
    if not result[0]:
        result_label.config(text="Invalid input", fg="#E74C3C")
        return
    _, weight, height, bmi, category = result
    color_map = {"Underweight": "#2E86AB", "Normal": "#2ECC71",
                 "Overweight": "#F39C12", "Obese": "#E74C3C"}
    result_label.config(text=f"BMI: {bmi:.2f}  ({category})", fg=color_map[category])


def on_save():
    name = name_entry.get().strip()
    if not name:
        save_status_label.config(text="Please enter a name.", fg="#E74C3C")
        return
    result = get_validated_bmi(weight_entry.get(), height_entry.get())
    if not result[0]:
        save_status_label.config(text="Invalid input. Cannot save.", fg="#E74C3C")
        return
    _, weight, height, bmi, category = result
    success = save_record(name, weight, height, bmi, category)
    if success:
        save_status_label.config(text="Saved!", fg="#2ECC71")
    else:
        save_status_label.config(text="Error saving record.", fg="#E74C3C")


def on_view_graph():
    name = name_entry.get().strip()
    if not name:
        save_status_label.config(text="Please enter a name to view graph.", fg="#E74C3C")
        return
    success, message = show_bmi_trend(name)
    save_status_label.config(text="" if success else message, fg="#E74C3C")


root = tk.Tk()
root.title("BMI Calculator")
root.geometry("360x420")
root.configure(bg="#F5F6FA")
root.resizable(False, False)

FONT_LABEL = ("Segoe UI", 10)
FONT_ENTRY = ("Segoe UI", 10)
FONT_BUTTON = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_RESULT = ("Segoe UI", 12, "bold")

title_label = tk.Label(root, text="BMI Calculator", font=FONT_TITLE, bg="#F5F6FA", fg="#2C3E50")
title_label.grid(row=0, column=0, columnspan=2, pady=(15, 10))

name_label = tk.Label(root, text="Name:", font=FONT_LABEL, bg="#F5F6FA")
name_label.grid(row=1, column=0, sticky="w", padx=(20, 5), pady=5)
name_entry = tk.Entry(root, font=FONT_ENTRY, width=20)
name_entry.grid(row=1, column=1, sticky="w", pady=5)

weight_label = tk.Label(root, text="Weight (kg):", font=FONT_LABEL, bg="#F5F6FA")
weight_label.grid(row=2, column=0, sticky="w", padx=(20, 5), pady=5)
weight_entry = tk.Entry(root, font=FONT_ENTRY, width=20)
weight_entry.grid(row=2, column=1, sticky="w", pady=5)

height_label = tk.Label(root, text="Height (m):", font=FONT_LABEL, bg="#F5F6FA")
height_label.grid(row=3, column=0, sticky="w", padx=(20, 5), pady=5)
height_entry = tk.Entry(root, font=FONT_ENTRY, width=20)
height_entry.grid(row=3, column=1, sticky="w", pady=5)

calculate_button = tk.Button(root, text="Calculate", font=FONT_BUTTON, bg="#3498DB", fg="white",
                              activebackground="#2980B9", relief="flat", command=on_calculate)
calculate_button.grid(row=4, column=0, columnspan=2, pady=(12, 5), ipadx=10, ipady=4)

result_label = tk.Label(root, text="", font=FONT_RESULT, bg="#F5F6FA")
result_label.grid(row=5, column=0, columnspan=2, pady=5)

save_button = tk.Button(root, text="Save", font=FONT_BUTTON, bg="#2ECC71", fg="white",
                          activebackground="#27AE60", relief="flat", command=on_save)
save_button.grid(row=6, column=0, columnspan=2, pady=5, ipadx=10, ipady=4)

save_status_label = tk.Label(root, text="", font=FONT_LABEL, bg="#F5F6FA")
save_status_label.grid(row=7, column=0, columnspan=2, pady=3)

view_graph_button = tk.Button(root, text="View Graph", font=FONT_BUTTON, bg="#9B59B6", fg="white",
                                activebackground="#8E44AD", relief="flat", command=on_view_graph)
view_graph_button.grid(row=8, column=0, columnspan=2, pady=(5, 15), ipadx=10, ipady=4)

if __name__ == "__main__":
    root.mainloop()