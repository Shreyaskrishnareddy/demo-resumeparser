import re

# Test with the exact spacing from Ahmad Qasem's resume
test_cases = [
    "I. Bachelor's Degree of Computer Engineering",        # 1 space (my test)
    "I.  Bachelor's Degree of Computer Engineering",       # 2 spaces
    "I.   Bachelor's Degree of Computer Engineering",      # 3 spaces
    "I.    Bachelor's Degree of Computer Engineering",     # 4 spaces (actual)
]

for test_case in test_cases:
    print(f"=== Testing: '{test_case}' ===")

    # Test the Roman numeral removal
    cleaned = re.sub(r'^[IVXLC]+\.\s*', '', test_case)
    print(f"After Roman numeral removal: '{cleaned}'")

    # Test the degree_of pattern
    degree_of_pattern = r'\b(?:bachelor\'?s?|master\'?s?|phd|ph\.d)\s+(?:degree\s+)?of\s+(.+?)(?:\s*,|\s*$)'
    degree_of_match = re.search(degree_of_pattern, cleaned, re.IGNORECASE)
    if degree_of_match:
        print(f"MATCH! Captured: '{degree_of_match.group(1)}'")
    else:
        print("NO MATCH!")
    print()