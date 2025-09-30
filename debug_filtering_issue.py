from fixed_comprehensive_parser import FixedComprehensiveParser
from docx import Document

# Debug why positions are being filtered out
parser = FixedComprehensiveParser()

doc = Document('Resume&Results/KrupakarReddy_SystemP.docx')
text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])

print("="*80)
print("🔍 DEBUGGING POSITION FILTERING")
print("="*80)

# Find experience section bounds
lines = text.split('\n')
experience_start = -1
experience_end = len(lines)

for i, line in enumerate(lines):
    line_upper = line.strip().upper().rstrip(':')
    if 'EXPERIENCE' in line_upper and len(line.strip().split()) <= 3:
        experience_start = i + 1
        print(f"\n📍 Experience section starts at line {i}: {repr(line.strip())}")
        break

# Get experience lines
experience_lines = lines[experience_start:experience_end] if experience_start != -1 else lines

print(f"   Processing {len(experience_lines)} lines")

# Call each parsing strategy separately
print("\n📊 STRATEGY RESULTS:")

# Strategy 1: Company-dash-location
result1 = parser._parse_company_dash_location_format(experience_lines)
print(f"\n1. Company-dash-location: {len(result1)} positions")
for pos in result1:
    print(f"   - {pos.get('JobTitle', {}).get('Raw', 'N/A')} at {pos.get('Employer', {}).get('Name', {}).get('Raw', 'N/A')}")

# Strategy 2: Traditional company format
result2 = parser._parse_traditional_company_format(experience_lines)
print(f"\n2. Traditional company format: {len(result2)} positions")
for pos in result2:
    print(f"   - {pos.get('JobTitle', {}).get('Raw', 'N/A')} at {pos.get('Employer', {}).get('Name', {}).get('Raw', 'N/A')}")

# Strategy 3: Job title first
result3 = parser._parse_job_title_first_format(experience_lines)
print(f"\n3. Job title first: {len(result3)} positions")
for pos in result3:
    print(f"   - {pos.get('JobTitle', {}).get('Raw', 'N/A')} at {pos.get('Employer', {}).get('Name', {}).get('Raw', 'N/A')}")

# Strategy 4: Company pipe date
result4 = parser._parse_company_pipe_date_format(experience_lines)
print(f"\n4. Company pipe date: {len(result4)} positions")
for pos in result4:
    print(f"   - {pos.get('JobTitle', {}).get('Raw', 'N/A')} at {pos.get('Employer', {}).get('Name', {}).get('Raw', 'N/A')}")

# Combine all
all_positions = result1 + result2 + result3 + result4
print(f"\n📦 TOTAL BEFORE FILTERING: {len(all_positions)} positions")

# Apply filtering
filtered_positions = parser._filter_and_dedupe_positions(all_positions)
print(f"📦 TOTAL AFTER FILTERING: {len(filtered_positions)} positions")

# Show what was filtered out
print(f"\n❌ FILTERED OUT: {len(all_positions) - len(filtered_positions)} positions")

if len(all_positions) != len(filtered_positions):
    print("\n🔍 ANALYZING WHAT WAS FILTERED:")
    for pos in all_positions:
        title = pos.get('JobTitle', {}).get('Raw', '').strip()
        company = pos.get('Employer', {}).get('Name', {}).get('Raw', '').strip()

        # Check if this was kept
        kept = any(
            p.get('JobTitle', {}).get('Raw', '') == title and
            p.get('Employer', {}).get('Name', {}).get('Raw', '') == company
            for p in filtered_positions
        )

        if not kept:
            print(f"   ❌ Filtered: '{title}' at '{company}'")
            # Check why
            is_invalid = parser._is_invalid_work_entry(title, company)
            print(f"      _is_invalid_work_entry: {is_invalid}")

print("\n" + "="*80)