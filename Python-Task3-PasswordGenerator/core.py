"""
core.py — Core logic for the Random Password Generator.

Contains all non-GUI logic: input validation, password generation,
and password strength scoring. Kept separate from the GUI
(password_generator.py) so this logic can be tested independently
from the console.
"""

import secrets
import string

# Characters considered visually ambiguous (easy to confuse when read/typed):
# 0 (zero), O (capital O), l (lowercase L), 1 (one)
AMBIGUOUS_CHARS = "0Ol1"

# Curated symbol set (deliberately restricted, not full punctuation,
# for readability and to avoid characters that cause issues in some systems)
SYMBOLS = "._@#$%&*"


def strip_ambiguous(pool, exclude_ambiguous):
    """
    Removes ambiguous characters (0, O, l, 1) from a character pool,
    if exclude_ambiguous is True. Otherwise returns the pool unchanged.
    """
    if exclude_ambiguous:
        for ch in AMBIGUOUS_CHARS:
            pool = pool.replace(ch, "")
    return pool


def validate_input(length, use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous):
    """
    Validates user input before generating a password.

    Returns:
        A human-readable error message (str) if input is invalid,
        or None if all checks pass.

    Checks performed:
        1. Minimum password length (8 characters)
        2. At least 2 character types must be selected
        3. (Defensive) Ensures excluding ambiguous characters hasn't
           emptied any selected pool, and that enough total characters
           remain to fill the requested length. Not reachable with the
           current character sets, but validated in case those sets
           change in the future.
    """
    if length < 8:
        return "Password length must be at least 8 characters."

    count_selected = sum([use_upper, use_lower, use_digits, use_symbols])
    if count_selected < 2:
        return "Select at least 2 character types."

    # Build each selected pool (with ambiguous chars stripped if requested)
    # and confirm nothing is left empty or too small.
    combined_pool = ""

    if use_upper:
        pool = strip_ambiguous(string.ascii_uppercase, exclude_ambiguous)
        if len(pool) == 0:
            return "Uppercase selected, but no characters remain after excluding ambiguous ones."
        combined_pool += pool

    if use_lower:
        pool = strip_ambiguous(string.ascii_lowercase, exclude_ambiguous)
        if len(pool) == 0:
            return "Lowercase selected, but no characters remain after excluding ambiguous ones."
        combined_pool += pool

    if use_digits:
        pool = strip_ambiguous(string.digits, exclude_ambiguous)
        if len(pool) == 0:
            return "Numbers selected, but no characters remain after excluding ambiguous ones."
        combined_pool += pool

    if use_symbols:
        pool = strip_ambiguous(SYMBOLS, exclude_ambiguous)
        if len(pool) == 0:
            return "Symbols selected, but no characters remain after excluding ambiguous ones."
        combined_pool += pool

    if len(combined_pool) < length:
        return "Not enough available characters to generate a password of this length after excluding ambiguous characters."

    return None


def check_strength(length, use_upper, use_lower, use_digits, use_symbols):
    """
    Scores password strength as "Weak", "Medium", or "Strong" based on
    two factors:
      - length (0-3 points: +1 each for >=8, >=12, >=16)
      - character-type diversity (0-4 points: +1 per selected type)

    Total score (0-7) maps to:
      0-3 -> Weak
      4-5 -> Medium
      6-7 -> Strong

    Both length AND diversity must be reasonably high to reach "Strong" —
    maxing out only one axis (e.g. very long but only 2 types, or short
    but all 4 types) caps out at "Medium".
    """
    length_score = 0
    if length >= 8:
        length_score += 1
    if length >= 12:
        length_score += 1
    if length >= 16:
        length_score += 1

    diversity_score = sum([use_upper, use_lower, use_digits, use_symbols])

    total_score = length_score + diversity_score

    if total_score <= 3:
        return "Weak"
    elif total_score <= 5:
        return "Medium"
    else:
        return "Strong"


def generate_password(length, use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous):
    """
    Generates a cryptographically secure random password matching the
    given criteria.

    Uses Python's `secrets` module (not `random`) for all randomness,
    since `random`'s Mersenne Twister PRNG is predictable and unsuitable
    for security-sensitive use.

    Generation strategy (to guarantee every selected type appears at
    least once, rather than leaving it to chance):
      1. Build each selected type's pool (ambiguous chars stripped if requested).
      2. Pick one guaranteed character from each selected type's own pool.
      3. Fill the remaining length randomly from the combined pool.
      4. Shuffle the full result (Fisher-Yates, using secrets.randbelow(),
         since `secrets` has no built-in shuffle function) so the
         guaranteed characters aren't predictably clustered at the start.
    """
    upper_pool = strip_ambiguous(string.ascii_uppercase, exclude_ambiguous)
    lower_pool = strip_ambiguous(string.ascii_lowercase, exclude_ambiguous)
    digits_pool = strip_ambiguous(string.digits, exclude_ambiguous)
    symbols_pool = strip_ambiguous(SYMBOLS, exclude_ambiguous)

    # Combined pool used for randomly filling the remaining characters
    character_pool = ""
    if use_upper:
        character_pool += upper_pool
    if use_lower:
        character_pool += lower_pool
    if use_digits:
        character_pool += digits_pool
    if use_symbols:
        character_pool += symbols_pool

    password_chars = []

    # Step 1: guarantee one character from each selected type
    if use_upper:
        password_chars.append(secrets.choice(upper_pool))
    if use_lower:
        password_chars.append(secrets.choice(lower_pool))
    if use_digits:
        password_chars.append(secrets.choice(digits_pool))
    if use_symbols:
        password_chars.append(secrets.choice(symbols_pool))

    # Step 2: fill remaining slots randomly from the combined pool
    remaining = length - len(password_chars)
    for _ in range(remaining):
        password_chars.append(secrets.choice(character_pool))

    # Step 3: Fisher-Yates shuffle (secure, unbiased) so guaranteed
    # characters aren't always at the front of the password
    for i in range(len(password_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

    # Step 4: join the list of characters into the final password string
    return "".join(password_chars)


if __name__ == "__main__":
    # Simple manual tests, run only when this file is executed directly
    # (not when imported by password_generator.py), thanks to this guard.

    # Test 1: valid input, no ambiguous exclusion
    error = validate_input(12, True, True, True, True, False)
    if error is not None:
        print("Error:", error)
    else:
        result = generate_password(12, True, True, True, True, False)
        print("Valid test (no exclusion):", result)

    # Test 2: valid input, WITH ambiguous exclusion
    error = validate_input(12, True, True, True, True, True)
    if error is not None:
        print("Error:", error)
    else:
        result = generate_password(12, True, True, True, True, True)
        print("Valid test (with exclusion):", result)

    # Test 3: invalid input (length too short)
    error = validate_input(5, True, True, True, True, False)
    if error is not None:
        print("Error:", error)
    else:
        result = generate_password(5, True, True, True, True, False)
        print("Valid test:", result)

    # Test 4: invalid input (only 1 type selected)
    error = validate_input(12, True, False, False, False, False)
    if error is not None:
        print("Error:", error)
    else:
        result = generate_password(12, True, False, False, False, False)
        print("Valid test:", result)

    # Test 5: check_strength known inputs
    print("Strength (8, upper+lower):", check_strength(8, True, True, False, False))
    print("Strength (16, upper+lower+digits):", check_strength(16, True, True, True, False))
    print("Strength (12, all 4 types):", check_strength(12, True, True, True, True))