from fixed_comprehensive_parser import FixedComprehensiveParser
from docx import Document

# Debug full parsing pipeline
doc = Document('Resume&Results/KrupakarReddy_SystemP.docx')
text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])

parser = FixedComprehensiveParser()

# Test individual parsing methods
lines = text.split('\n')
experience_start = -1
for i, line in enumerate(lines):
    if 'EXPERIENCE DETAILS' in line.upper():
        experience_start = i + 1
        break

if experience_start != -1:
    experience_lines = lines[experience_start:experience_start+200]
    
    print('=== TESTING ALL PARSING METHODS ===')
    
    # Method 1: Company pipe date format
    pos1 = parser._parse_company_pipe_date_format(experience_lines)
    print(f'Company pipe format: {len(pos1)} positions')
    
    # Method 2: Company dash location format
    pos2 = parser._parse_company_dash_location_format(experience_lines)
    print(f'Company dash location: {len(pos2)} positions')
    
    # Method 3: Traditional company format  
    pos3 = parser._parse_traditional_company_format(experience_lines)
    print(f'Traditional company: {len(pos3)} positions')
    
    # Method 4: Job title first format
    pos4 = parser._parse_job_title_first_format(experience_lines)
    print(f'Job title first: {len(pos4)} positions')
    
    all_positions = pos1 + pos2 + pos3 + pos4
    print(f'Total before filtering: {len(all_positions)} positions')
    
    # Test filtering
    filtered = parser._filter_and_dedupe_positions(all_positions)
    print(f'After filtering: {len(filtered)} positions')
    
    print('\n=== FILTERED POSITIONS ===')
    for i, pos in enumerate(filtered, 1):
        print(f'{i}. {repr(pos.get("JobTitle", {}).get("Raw", "None"))} at {repr(pos.get("Employer", {}).get("Name", {}).get("Raw", "None"))}')
