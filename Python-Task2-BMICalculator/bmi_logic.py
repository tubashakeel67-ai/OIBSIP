"""
bmi_logic.py
Core BMI logic — no GUI or database code here.
"""


def validate_input(weight_str, height_str):
    """Checks if weight/height are valid positive numbers."""
    try:
        weight = float(weight_str)
        height = float(height_str)
    except ValueError:
        return False, None, None

    if weight <= 0 or height <= 0:
        return False, None, None

    if not (1 <= weight <= 300):
        return False, None, None
    if not (0.5 <= height <= 2.5):
        return False, None, None

    return True, weight, height


def calculate_bmi(weight, height):
    """BMI formula: weight / height^2"""
    return weight / (height ** 2)


def classify_bmi(bmi_value):
    """Maps BMI to health category."""
    if bmi_value < 18.5:
        return "Underweight"
    elif bmi_value < 25:
        return "Normal"
    elif bmi_value < 30:
        return "Overweight"
    else:
        return "Obese"


def main_console_loop():
    """Runs the CLI loop until user quits."""
    print("=" * 40)
    print("        BMI CALCULATOR")
    print("=" * 40)

    while True:
        weight_str = input("\nEnter your weight in kg: ")
        height_str = input("Enter your height in meters: ")

        is_valid, weight, height = validate_input(weight_str, height_str)

        if not is_valid:
            print("❌ Invalid input. Please enter positive numeric values.")
            continue

        bmi = calculate_bmi(weight, height)
        category = classify_bmi(bmi)

        print(f"\nYour BMI is: {bmi:.2f}")
        print(f"Category: {category}")

        again = input("\nCalculate another? (y/n): ").strip().lower()
        if again != "y":
            print("\nGoodbye! Stay healthy.")
            break


if __name__ == "__main__":
    main_console_loop()