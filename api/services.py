# api/services.py
import hashlib
from collections import Counter

def analyze_string_value(value: str) -> dict:
    """
    Takes a string and computes all its required properties.
    Returns a dictionary containing the properties.
    """
    # Sanitize and prepare the string for palindrome check
    lower_value = value.lower()
    
    # Calculate all properties
    length = len(value)
    is_palindrome = lower_value == lower_value[::-1]
    unique_characters = len(set(value))
    word_count = len(value.split())
    sha256_hash = hashlib.sha256(value.encode()).hexdigest()
    character_frequency_map = dict(Counter(value))
    
    return {
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_characters,
        "word_count": word_count,
        "sha256_hash": sha256_hash,
        "character_frequency_map": character_frequency_map,
    }