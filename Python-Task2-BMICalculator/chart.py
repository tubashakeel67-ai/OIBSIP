"""
chart.py
matplotlib BMI trend graph, built from stored history in database.py.
"""
import matplotlib.pyplot as plt
from database import get_user_history


def show_bmi_trend(name):
    records = get_user_history(name)

    if not records:
        return False, f"No history found for '{name}'."

    dates = [row[6] for row in records]
    bmi_values = [row[4] for row in records]

    plt.figure(figsize=(8, 5))
    plt.plot(dates, bmi_values, marker="o", linestyle="-", color="blue")
    plt.title(f"BMI Trend for {name}")
    plt.xlabel("Date")
    plt.ylabel("BMI")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

    return True, "Graph displayed."