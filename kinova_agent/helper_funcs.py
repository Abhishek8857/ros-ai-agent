import re

WORD_TO_NUMBER = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}


def word_to_num (query):
    """
    Converts words representing numbers to their numerical equivalent.
    Supports small numbers and phrases like "By 2 Units"
    """
    
    words = query.lower().strip()
    
    # Check if the input contains numerical digits
    match = re.search(r'\b\d+\b', words)
    if match:
        number = int(match.group())
        if 1 <= number <= 10:
            return number
        else:
            raise ValueError("Number out of range. Only numbers from 1 to 10 are allowed.")
    
    # Check for word representation of numbers
    tokens = words.split()
    for word in tokens:
        if word in WORD_TO_NUMBER:
            return WORD_TO_NUMBER[word]
    
    raise ValueError("Invalid query. Please provide a number between 1 and 10")


