import re

# Test the exact pattern and string that's failing
pattern = r'\b(?:bachelor\'?s?|master\'?s?|phd|ph\.d)\s+(?:degree\s+)?of\s+(.+?)(?:\s*,|\s*$)'
test_string = "Bachelor's Degree of Computer Engineering"

print(f"Pattern: {pattern}")
print(f"Test string: '{test_string}'")
print(f"String length: {len(test_string)}")
print(f"String repr: {repr(test_string)}")

# Test the match
match = re.search(pattern, test_string, re.IGNORECASE)
print(f"Match result: {match}")

if match:
    print(f"Captured group: '{match.group(1)}'")
    print(f"Full match: '{match.group(0)}'")
else:
    print("NO MATCH!")

# Let's break down the pattern step by step
print(f"\n=== BREAKING DOWN THE PATTERN ===")

# Test each part
bachelor_part = r'\b(?:bachelor\'?s?|master\'?s?|phd|ph\.d)'
print(f"Bachelor part match: {re.search(bachelor_part, test_string, re.IGNORECASE)}")

degree_part = r'\s+(?:degree\s+)?'
print(f"After bachelor, looking for degree part in: '{test_string[9:]}'")
remainder_after_bachelor = test_string[9:]  # After "Bachelor'"
print(f"Does '{remainder_after_bachelor}' match degree pattern? {re.search(degree_part, remainder_after_bachelor)}")

of_part = r'of\s+'
print(f"Looking for 'of' part in: '{remainder_after_bachelor}'")
of_match_pos = re.search(of_part, remainder_after_bachelor)
print(f"Of match: {of_match_pos}")

# Test simpler patterns to isolate the issue
simple_pattern = r'bachelor.*of\s+(.+?)$'
simple_match = re.search(simple_pattern, test_string, re.IGNORECASE)
print(f"\nSimple pattern match: {simple_match}")
if simple_match:
    print(f"Simple captured: '{simple_match.group(1)}'")

# Test even simpler
very_simple = r'of\s+(.+?)$'
very_simple_match = re.search(very_simple, test_string, re.IGNORECASE)
print(f"Very simple pattern match: {very_simple_match}")
if very_simple_match:
    print(f"Very simple captured: '{very_simple_match.group(1)}'")

# Test character by character what we have
print(f"\n=== CHARACTER ANALYSIS ===")
for i, char in enumerate(test_string):
    print(f"{i:2d}: '{char}' (ord {ord(char)})")

# Check if there are any hidden characters
print(f"\nString bytes: {test_string.encode('utf-8')}")

# Test without the word boundary
no_word_boundary = r'(?:bachelor\'?s?|master\'?s?|phd|ph\.d)\s+(?:degree\s+)?of\s+(.+?)(?:\s*,|\s*$)'
no_wb_match = re.search(no_word_boundary, test_string, re.IGNORECASE)
print(f"\nWithout word boundary: {no_wb_match}")
if no_wb_match:
    print(f"No WB captured: '{no_wb_match.group(1)}'")