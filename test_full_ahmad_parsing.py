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
print(f"Success: {result.get('success', False)}")

if result.get('success'):
    parsed_data = result.get('parsed_data', {})

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
    print(f"Work Experience: {len(parsed_data.get('WorkExperience', []))}")
    print(f"Certifications: {len(parsed_data.get('Certifications', []))}")

else:
    print(f"Error: {result.get('error', 'Unknown error')}")