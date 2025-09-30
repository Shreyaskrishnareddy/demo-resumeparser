from fixed_comprehensive_parser import FixedComprehensiveParser
from docx import Document

# Debug work experience extraction for Krupakar
doc = Document('Resume&Results/KrupakarReddy_SystemP.docx')
text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])

parser = FixedComprehensiveParser()

print("="*80)
print("🔍 KRUPAKAR WORK EXPERIENCE - DEBUG ANALYSIS")
print("="*80)

# Expected work experiences from the resume:
print("\n📋 EXPECTED WORK EXPERIENCES:")
expected_positions = [
    ("Cardinal Health", "Oct 2023 – Present", "Mainframe Z/os System Programmer"),
    ("Prudential Financial", "Jan 2022 - Sep 2023", "Mainframe Z/os System Programmer"),
    ("State of Hartford", "Aug 2019 - Dec 2021", "Role not shown in preview"),
    ("Walmart", "Mar 2015 to Jun 2017", "Software Engineer /Mainframe Developer"),
    ("Syntel", "Jul 2010 – Mar 2012", "Web Developer")
]

for i, (company, dates, title) in enumerate(expected_positions, 1):
    print(f"   {i}. {company} ({dates}) - {title}")

# Test the extraction
print("\n📊 ACTUAL EXTRACTION:")
result = parser._extract_experience_fixed(text)
print(f"   Total positions extracted: {len(result)}")

for i, pos in enumerate(result, 1):
    print(f"\n   Position {i}:")
    print(f"      Title: {pos.get('JobTitle', {}).get('Raw', 'N/A')}")
    print(f"      Company: {pos.get('Employer', {}).get('Name', {}).get('Raw', 'N/A')}")
    print(f"      Start: {pos.get('StartDate', {}).get('Date', 'N/A')}")
    print(f"      End: {pos.get('EndDate', {}).get('Date', 'N/A')}")

# Check the raw text for company patterns
print("\n\n🔍 SEARCHING FOR COMPANY-DATE PATTERNS IN TEXT:")
lines = text.split('\n')

for i, line in enumerate(lines):
    line_clean = line.strip()
    # Look for the pattern "Company, Location||Date - Date"
    if '||' in line_clean:
        print(f"\nFound || pattern at line {i}:")
        print(f"   {repr(line_clean)}")

        # Show context
        context_start = max(0, i-2)
        context_end = min(len(lines), i+5)
        print(f"   Context:")
        for j in range(context_start, context_end):
            marker = ">>>" if j == i else "   "
            print(f"{marker} {j}: {lines[j].strip()[:100]}")

print("\n" + "="*80)