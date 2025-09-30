import re

# Test the exact _parse_degree_string logic
def debug_parse_degree_string(degree_str: str):
    print(f"=== DEBUGGING: '{degree_str}' ===")

    # Clean the degree string first
    cleaned_degree = degree_str.strip()
    print(f"After strip: '{cleaned_degree}'")

    # Remove Roman numerals and bullets at the beginning (I., II., etc.)
    cleaned_degree = re.sub(r'^[IVXLC]+\.\s*', '', cleaned_degree)
    print(f"After Roman numeral removal: '{cleaned_degree}'")

    cleaned_degree = re.sub(r'^[•\-\*]\s*', '', cleaned_degree)
    print(f"After bullet removal: '{cleaned_degree}'")

    result = {'Degree': cleaned_degree, 'DegreeType': '', 'Major': '', 'FieldOfStudy': ''}
    print(f"Initial result: {result}")

    # Extract degree type
    if re.search(r'\bphd\b|\bph\.d\b|\bdoctorate\b', cleaned_degree, re.IGNORECASE):
        result['DegreeType'] = 'PhD'
        print("Matched PhD degree type")
    elif re.search(r'\bmaster|\bmba\b', cleaned_degree, re.IGNORECASE):
        result['DegreeType'] = 'Master'
        print("Matched Master degree type")
    elif re.search(r'\bbachelor', cleaned_degree, re.IGNORECASE):
        result['DegreeType'] = 'Bachelor'
        print("Matched Bachelor degree type")

    print(f"After degree type: {result}")

    # Extract field of study/major
    # Pattern 1: "Master of Business Administration MBA – Project Management"
    if ' – ' in cleaned_degree or ' - ' in cleaned_degree:
        print("Testing dash pattern...")
        parts = re.split(r'\s*[–-]\s*', cleaned_degree, 1)
        print(f"Dash split parts: {parts}")
        if len(parts) > 1:
            result['Major'] = parts[1].strip()
            result['FieldOfStudy'] = parts[1].strip()
            print(f"Set Major/FieldOfStudy from dash: '{parts[1].strip()}'")

    # Pattern 2: "Bachelor's Degree of Computer Engineering"
    print("Testing 'degree of' pattern...")
    degree_of_pattern = r'\b(?:bachelor\'?s?|master\'?s?|phd|ph\.d)\s+(?:degree\s+)?of\s+(.+?)(?:\s*,|\s*$)'
    print(f"Pattern: {degree_of_pattern}")
    degree_of_match = re.search(degree_of_pattern, cleaned_degree, re.IGNORECASE)
    if degree_of_match:
        print(f"MATCH! Captured: '{degree_of_match.group(1)}'")
        if not result['Major']:
            result['Major'] = degree_of_match.group(1).strip()
            result['FieldOfStudy'] = degree_of_match.group(1).strip()
            print(f"Set Major/FieldOfStudy from degree_of: '{degree_of_match.group(1).strip()}'")
        else:
            print("Major already set, skipping")
    else:
        print("NO MATCH for degree_of pattern")

    # Pattern 3: "Bachelor of Computer Science"
    print("Testing 'of' pattern...")
    of_pattern = r'\b(?:bachelor|master|phd|ph\.d)\s+(?:of\s+)?(.+?)(?:\s*,|\s*$)'
    print(f"Pattern: {of_pattern}")
    of_match = re.search(of_pattern, cleaned_degree, re.IGNORECASE)
    if of_match:
        print(f"MATCH! Captured: '{of_match.group(1)}'")
        if not result['Major']:
            result['Major'] = of_match.group(1).strip()
            result['FieldOfStudy'] = of_match.group(1).strip()
            print(f"Set Major/FieldOfStudy from of: '{of_match.group(1).strip()}'")
        else:
            print("Major already set, skipping")
    else:
        print("NO MATCH for of pattern")

    # Pattern 4: "PHD in Corporate Innovation and Entrepreneurship"
    print("Testing 'in' pattern...")
    in_pattern = r'\bin\s+(.+?)(?:\s*,|\s*$)'
    print(f"Pattern: {in_pattern}")
    in_match = re.search(in_pattern, cleaned_degree, re.IGNORECASE)
    if in_match:
        print(f"MATCH! Captured: '{in_match.group(1)}'")
        if not result['Major']:
            result['Major'] = in_match.group(1).strip()
            result['FieldOfStudy'] = in_match.group(1).strip()
            print(f"Set Major/FieldOfStudy from in: '{in_match.group(1).strip()}'")
        else:
            print("Major already set, skipping")
    else:
        print("NO MATCH for in pattern")

    print(f"FINAL RESULT: {result}")
    return result

# Test the problematic case
test_case = "I. Bachelor's Degree of Computer Engineering"
debug_parse_degree_string(test_case)