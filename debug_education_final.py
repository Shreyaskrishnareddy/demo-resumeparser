from fixed_comprehensive_parser import FixedComprehensiveParser
import json
import fitz

# Debug the education validation issue
parser = FixedComprehensiveParser()

# Read PDF text
doc = fitz.open('Resume&Results/Ahmad Qasem-Resume.pdf')
text = ""
for page in doc:
    text += page.get_text()
doc.close()

# Parse full resume
result = parser.parse_resume(text, 'Ahmad Qasem-Resume.pdf')
education = result.get('Education', [])

print("=== EDUCATION VALIDATION DEBUG ===")
print(f"Number of education entries: {len(education)}")

if education:
    entry = education[0]
    print(f"\nEducation Entry:")
    for key, value in entry.items():
        print(f"  {key}: {repr(value)}")

    print(f"\n=== VALIDATION CHECKS ===")
    print(f"Major == 'Computer Engineering': {entry.get('Major') == 'Computer Engineering'}")
    print(f"Major value: {repr(entry.get('Major'))}")

    expected_degree = "Bachelor's Degree of Computer Engineering"
    print(f"Degree == expected: {entry.get('Degree') == expected_degree}")
    print(f"Degree value: {repr(entry.get('Degree'))}")

    print(f"Institution == 'Applied Science University': {entry.get('Institution') == 'Applied Science University'}")
    print(f"Institution value: {repr(entry.get('Institution'))}")

    print(f"GraduationYear == '2014': {entry.get('GraduationYear') == '2014'}")
    print(f"GraduationYear value: {repr(entry.get('GraduationYear'))}")

    # Check the overall validation condition
    education_valid = (
        len(education) == 1 and
        entry.get('Major') == 'Computer Engineering' and
        entry.get('Degree') == "Bachelor's Degree of Computer Engineering" and
        entry.get('Institution') == 'Applied Science University' and
        entry.get('GraduationYear') == '2014'
    )
    print(f"\nOverall education valid: {education_valid}")
else:
    print("No education entries found!")

# Also test the direct extraction
print(f"\n=== DIRECT EXTRACTION TEST ===")
direct_education = parser._extract_education_comprehensive(text)
print(f"Direct extraction found: {len(direct_education)} entries")
if direct_education:
    direct_entry = direct_education[0]
    print(f"Direct Major: {repr(direct_entry.get('Major'))}")
    print(f"Direct FieldOfStudy: {repr(direct_entry.get('FieldOfStudy'))}")