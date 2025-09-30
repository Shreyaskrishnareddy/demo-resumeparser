from fixed_comprehensive_parser import FixedComprehensiveParser
import json
import fitz

# Test full parsing of Ahmad Qasem resume
parser = FixedComprehensiveParser()

# Read PDF text first
doc = fitz.open('Resume&Results/Ahmad Qasem-Resume.pdf')
text = ""
for page in doc:
    text += page.get_text()
doc.close()

print(f"PDF text length: {len(text)} characters")

# Parse the resume
result = parser.parse_resume(text, 'Ahmad Qasem-Resume.pdf')

print("=== FULL AHMAD QASEM PARSING RESULT ===")

# The parse_resume method returns the parsed data directly
parsed_data = result

# Check languages specifically
languages = parsed_data.get('Languages', [])
print(f"\n=== LANGUAGES SECTION ===")
print(f"Number of languages: {len(languages)}")
if languages:
    for i, lang in enumerate(languages, 1):
        print(f"{i}. {json.dumps(lang, indent=2)}")
else:
    print("No languages found!")

# Also check other sections for comparison
print(f"\n=== OTHER SECTIONS SUMMARY ===")
print(f"Education entries: {len(parsed_data.get('Education', []))}")
print(f"Skills: {len(parsed_data.get('ListOfSkills', []))}")
print(f"Work Experience: {len(parsed_data.get('ListOfExperiences', []))}")
print(f"Certifications: {len(parsed_data.get('Certifications', []))}")

# Show parsing metadata
metadata = parsed_data.get('ParsingMetadata', {})
print(f"\n=== PARSING METADATA ===")
print(f"Parser version: {metadata.get('parser_version', 'unknown')}")
print(f"Processing time: {metadata.get('processing_time', 0):.3f}s")
print(f"Accuracy score: {metadata.get('accuracy_score', 0)}")

# Show some education details if found
education = parsed_data.get('Education', [])
if education:
    print(f"\n=== EDUCATION DETAILS ===")
    for i, edu in enumerate(education, 1):
        print(f"{i}. Degree: {edu.get('Degree', 'N/A')}")
        print(f"   Major: {edu.get('Major', 'N/A')}")
        print(f"   Institution: {edu.get('Institution', 'N/A')}")
        print(f"   Year: {edu.get('GraduationYear', 'N/A')}")