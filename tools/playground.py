from rapidfuzz import process, fuzz

from tools.app import fetch_json


# ----- Techniques -----
# Normalization:
#
# Standardize inputs and items by removing case sensitivity and non-alphanumeric characters.
# Exact Matching:
#
# Prioritize matches that directly align with the input text.
# Soundex Phonetic Matching:
#
# Match phonetically similar words to handle OCR errors or misspellings.
# Tokenization and Substring Matching:
#
# Handle compound or multi-word names by breaking them into tokens and checking partial matches.
# Fuzzy Matching:
#
# Provide a fallback for distant matches when exact or token matches fail.
# Weighted Scoring:
#
# Combine results from multiple techniques to prioritize better matches.
# --------------------------------------------------------------------------------------------
# ----- Topologies -----
# Hierarchical Matching Topology:
#
# Sequentially apply matching techniques in a prioritized order.
# Multi-Technique Scoring Topology:
#
# Combine scores from various techniques to identify the most relevant match.
# Dynamic Weighting Topology:
#
# Dynamically adjust scores based on the confidence and relevance of each matching method.


def soundex(text):
    """
    Compute the Soundex phonetic encoding for a text.
    Helps in matching phonetically similar strings.
    """
    text = text.lower()
    soundex_code = text[0].upper()
    dictionary = {
        "a": "", "e": "", "i": "", "o": "", "u": "", "h": "", "w": "", "y": "",
        "b": "1", "f": "1", "p": "1", "v": "1",
        "c": "2", "g": "2", "j": "2", "k": "2", "q": "2", "s": "2", "x": "2", "z": "2",
        "d": "3", "t": "3",
        "l": "4",
        "m": "5", "n": "5",
        "r": "6",
    }

    # Encode based on the dictionary
    for char in text[1:]:
        code = dictionary.get(char, "")
        if not soundex_code.endswith(code):
            soundex_code += code

    # Pad to ensure a length of 4
    soundex_code = soundex_code[:4].ljust(4, "0")
    return soundex_code


def get_best_match(input_text, items):
    """
    Determine the most likely match for an input text from a list of items.

    :param input_text: The text to match (e.g., OCR output).
    :param items: A list of valid items to match against (e.g., heroes, maps).
    :return: The best-matched item from the list.
    """
    input_text = input_text.lower().strip()
    normalized_items = {item.lower(): item for item in items}  # Keep original casing
    scores = {}

    # Step 1: Exact match priority
    if input_text in normalized_items:
        return normalized_items[input_text]

    # Step 2: Soundex for phonetically similar matches
    input_soundex = soundex(input_text)
    for item in items:
        if input_soundex == soundex(item):
            scores[item] = max(scores.get(item, 0), 90)

    # Step 3: Substring and token matching
    for item in items:
        tokens = item.lower().split()
        if any(input_text in token for token in tokens):
            scores[item] = max(scores.get(item, 0), 95)

    # Step 4: Fuzzy matching fallback
    fuzzy_match = process.extractOne(input_text, items, scorer=fuzz.ratio)
    if fuzzy_match:
        matched_item, fuzzy_score, _ = fuzzy_match
        scores[matched_item] = max(scores.get(matched_item, 0), fuzzy_score)

    # Step 5: Return the item with the highest score
    if scores:
        return max(scores, key=scores.get)

    return "Unknown"  # Fallback if no matches are found


# Example usage
api = "https://overfast-api.tekrop.fr"
maps = [entry["name"] for entry in fetch_json(f"{api}/maps") if len(entry["gamemodes"]) == 1]
heroes = [entry["name"] for entry in fetch_json(f"{api}/heroes")]
examples_maps = ["alto", "Gib", "rial", "watch", "ani", "api", "run", "ard"]
examples_heroes = ["dva", "ball", "soldier", "76", "queen", "kiri", "wifeleaver", "rein", "soj", "torb", "zen"]
for ocr_output in examples_maps:
    result = get_best_match(ocr_output, maps)
    print(f"OCR Output: '{ocr_output}' -> Matched Map: {result}")

for ocr_output in examples_heroes:
    result = get_best_match(ocr_output, heroes)
    print(f"OCR Output: '{ocr_output}' -> Matched Hero: {result}")
