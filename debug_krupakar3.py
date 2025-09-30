from fixed_comprehensive_parser import FixedComprehensiveParser
from docx import Document

# Debug the full _extract_experience_fixed method
doc = Document('Resume&Results/KrupakarReddy_SystemP.docx')
text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])

parser = FixedComprehensiveParser()

print('=== TESTING FULL _extract_experience_fixed METHOD ===')
experience = parser._extract_experience_fixed(text)

print(f'Full method returned: {len(experience)} positions')
for i, pos in enumerate(experience, 1):
    print(f'{i}. {repr(pos.get("JobTitle", {}).get("Raw", "None"))} at {repr(pos.get("Employer", {}).get("Name", {}).get("Raw", "None"))}')
    print(f'   Start: {pos.get("StartDate", {}).get("Date", "None")}')
    print(f'   End: {pos.get("EndDate", {}).get("Date", "None")}')

# Also test the section detection
lines = text.split('\n')
print(f'\n=== SECTION DETECTION DEBUG ===')
for i, line in enumerate(lines):
    line_upper = line.strip().upper().rstrip(':')
    if 'EXPERIENCE' in line_upper and len(line.strip()) < 50:
        print(f'Line {i}: "{line.strip()}" -> "{line_upper}"')
