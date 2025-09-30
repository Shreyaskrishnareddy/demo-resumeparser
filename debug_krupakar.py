from fixed_comprehensive_parser import FixedComprehensiveParser
from docx import Document

# Debug the company pipe parsing specifically
doc = Document('Resume&Results/KrupakarReddy_SystemP.docx')
text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])

parser = FixedComprehensiveParser()

# Extract experience section manually to debug
lines = text.split('\n')
experience_start = -1

for i, line in enumerate(lines):
    if 'EXPERIENCE DETAILS' in line.upper():
        experience_start = i + 1
        break

if experience_start != -1:
    experience_lines = lines[experience_start:experience_start+50]  # First 50 lines
    
    print('=== FIRST 20 LINES OF EXPERIENCE SECTION ===')
    for i, line in enumerate(experience_lines[:20]):
        marker = '>>>' if '||' in line else '   '
        print(f'{marker} {i:2d}: {repr(line)}')
        
    print('\n=== TESTING COMPANY PIPE DATE FORMAT ===')
    positions = parser._parse_company_pipe_date_format(experience_lines)
    
    print(f'Found {len(positions)} positions')
    for i, pos in enumerate(positions, 1):
        print(f'{i}. Job Title: {repr(pos.get("JobTitle", {}).get("Raw", "None"))}')
        print(f'   Company: {repr(pos.get("Employer", {}).get("Name", {}).get("Raw", "None"))}')
