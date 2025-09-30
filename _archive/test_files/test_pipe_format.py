from fixed_comprehensive_parser import FixedComprehensiveParser
from docx import Document

# Test the pipe format parsing directly
parser = FixedComprehensiveParser()

# Get text lines
doc = Document('Resume&Results/KrupakarReddy_SystemP.docx')
text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
lines = text.split('\n')

print("="*80)
print("🧪 TESTING PIPE FORMAT PARSING")
print("="*80)

# Test the method directly
result = parser._parse_company_pipe_date_format(lines)

print(f"\nDirect method call result: {len(result)} positions")
for i, pos in enumerate(result, 1):
    print(f"\n{i}. {pos.get('JobTitle', {}).get('Raw', 'N/A')}")
    print(f"   Company: {pos.get('Employer', {}).get('Name', {}).get('Raw', 'N/A')}")
    print(f"   Start: {pos.get('StartDate', {}).get('Date', 'N/A')}")
    print(f"   End: {pos.get('EndDate', {}).get('Date', 'N/A')}")

# Test individual helper methods
print("\n" + "="*80)
print("🧪 TESTING HELPER METHODS")
print("="*80)

test_line = "Cardinal Health, Remote, United States||Oct 2023 – Present"
print(f"\nTest line: {repr(test_line)}")

# Test _contains_date_range
has_date = parser._contains_date_range(test_line)
print(f"_contains_date_range: {has_date}")

if '||' in test_line:
    company_part, date_part = test_line.split('||', 1)
    print(f"\nCompany part: {repr(company_part)}")
    print(f"Date part: {repr(date_part)}")

    # Test _parse_company_location
    company_info = parser._parse_company_location(company_part.strip())
    print(f"\n_parse_company_location result:")
    print(f"   Company: {repr(company_info['company'])}")
    print(f"   Location: {repr(company_info['location'])}")

    # Test _parse_date_range_enhanced
    date_info = parser._parse_date_range_enhanced(date_part.strip())
    print(f"\n_parse_date_range_enhanced result:")
    print(f"   Start: {repr(date_info['start_date'])}")
    print(f"   End: {repr(date_info['end_date'])}")
    print(f"   Is current: {date_info['is_current']}")

print("\n" + "="*80)