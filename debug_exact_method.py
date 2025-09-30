from fixed_comprehensive_parser import FixedComprehensiveParser

# Create parser instance
parser = FixedComprehensiveParser()

# Test the exact degree line from Ahmad Qasem's resume
exact_degree_line = "I.    Bachelor's Degree of Computer Engineering"

print(f"=== Testing exact method with: '{exact_degree_line}' ===")

# Call the actual method from the parser
result = parser._parse_degree_string(exact_degree_line)

print(f"Result: {result}")

# Test each field
print(f"Degree: '{result.get('Degree', 'MISSING')}'")
print(f"DegreeType: '{result.get('DegreeType', 'MISSING')}'")
print(f"Major: '{result.get('Major', 'MISSING')}'")
print(f"FieldOfStudy: '{result.get('FieldOfStudy', 'MISSING')}'")

# Also test with cleaner input to see if that works
clean_line = "Bachelor's Degree of Computer Engineering"
print(f"\n=== Testing with cleaned line: '{clean_line}' ===")
result2 = parser._parse_degree_string(clean_line)
print(f"Result: {result2}")
print(f"Major: '{result2.get('Major', 'MISSING')}'")
print(f"FieldOfStudy: '{result2.get('FieldOfStudy', 'MISSING')}'")

# Let me also manually test the regex steps
import re
print(f"\n=== Manual regex testing ===")

# Step 1: Clean
cleaned_degree = exact_degree_line.strip()
print(f"After strip: '{cleaned_degree}'")

# Step 2: Remove Roman numerals
cleaned_degree = re.sub(r'^[IVXLC]+\.\s*', '', cleaned_degree)
print(f"After Roman numeral removal: '{cleaned_degree}'")

# Step 3: Test the degree_of pattern
degree_of_pattern = r'\b(?:bachelor\'?s?|master\'?s?|phd|ph\.d)\s+(?:degree\s+)?of\s+(.+?)(?:\s*,|\s*$)'
match = re.search(degree_of_pattern, cleaned_degree, re.IGNORECASE)
if match:
    print(f"Regex match found: '{match.group(1)}'")
else:
    print("No regex match!")

# Check if the pattern looks right
print(f"Pattern being used: {degree_of_pattern}")
print(f"Testing against: '{cleaned_degree}'")