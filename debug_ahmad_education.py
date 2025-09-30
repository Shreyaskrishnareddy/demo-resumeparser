from fixed_comprehensive_parser import FixedComprehensiveParser
import fitz  # PyMuPDF

# Test the actual Ahmad Qasem resume education extraction
resume_path = 'Resume&Results/Ahmad Qasem-Resume.pdf'

# Read PDF
doc = fitz.open(resume_path)
text = ""
for page in doc:
    text += page.get_text()
doc.close()

parser = FixedComprehensiveParser()

print("=== TESTING AHMAD QASEM EDUCATION EXTRACTION ===")

# Test the education extraction
education = parser._extract_education_comprehensive(text)

print(f"Found {len(education)} education entries:")
for i, entry in enumerate(education, 1):
    print(f"\n{i}. Education Entry:")
    print(f"   Degree: {repr(entry.get('Degree', 'None'))}")
    print(f"   DegreeType: {repr(entry.get('DegreeType', 'None'))}")
    print(f"   Major: {repr(entry.get('Major', 'None'))}")
    print(f"   FieldOfStudy: {repr(entry.get('FieldOfStudy', 'None'))}")
    print(f"   Institution: {repr(entry.get('Institution', 'None'))}")
    print(f"   GraduationYear: {repr(entry.get('GraduationYear', 'None'))}")

# Now let's also add debugging directly to the parser method
print(f"\n=== TESTING DEGREE STRING PARSING ON ACTUAL TEXT ===")

# Find the degree lines in the text
lines = text.split('\n')
for i, line in enumerate(lines):
    if 'Bachelor' in line and 'Computer Engineering' in line:
        print(f"Found degree line {i}: '{line.strip()}'")

        # Test the _parse_degree_string directly on this line
        degree_info = parser._parse_degree_string(line.strip())
        print(f"Parsed result: {degree_info}")
        print()