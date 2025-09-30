from fixed_comprehensive_parser import FixedComprehensiveParser
import json
import fitz

# Debug work experience for Ahmad Qasem
parser = FixedComprehensiveParser()

# Read PDF text
doc = fitz.open('Resume&Results/Ahmad Qasem-Resume.pdf')
text = ""
for page in doc:
    text += page.get_text()
doc.close()

# Parse full resume to get work experience
result = parser.parse_resume(text, 'Ahmad Qasem-Resume.pdf')
work_experience = result.get('ListOfExperiences', [])

print("=== AHMAD QASEM WORK EXPERIENCE ANALYSIS ===")
print(f"Total work experience entries found: {len(work_experience)}")
print()

# Analyze each work experience entry
print("=== ALL WORK EXPERIENCE ENTRIES ===")
for i, entry in enumerate(work_experience, 1):
    print(f"{i}. Job Title: {repr(entry.get('JobTitle', 'N/A'))}")
    print(f"   Company: {repr(entry.get('Employer', 'N/A'))}")
    print(f"   Start Date: {repr(entry.get('StartDate', 'N/A'))}")
    print(f"   End Date: {repr(entry.get('EndDate', 'N/A'))}")
    print(f"   Location: {repr(entry.get('Location', 'N/A'))}")
    print(f"   Duration: {repr(entry.get('Duration', 'N/A'))}")
    print(f"   Description: {repr(entry.get('Description', 'N/A'))}")
    print()

# Look for garbage indicators
print("=== GARBAGE ENTRY ANALYSIS ===")

garbage_entries = []
for i, entry in enumerate(work_experience, 1):
    job_title = str(entry.get('JobTitle', '')).strip()
    company = str(entry.get('Employer', '')).strip()
    description = str(entry.get('Description', '')).strip()

    # Check for garbage indicators
    is_garbage = False
    reasons = []

    # Empty or very short job title
    if not job_title or len(job_title) < 3:
        is_garbage = True
        reasons.append("Empty or very short job title")

    # Empty or very short company
    if not company or len(company) < 3:
        is_garbage = True
        reasons.append("Empty or very short company")

    # Email addresses in job title or company
    if '@' in job_title or '@' in company:
        is_garbage = True
        reasons.append("Contains email address")

    # Meaningless job titles
    meaningless_titles = ['reference', 'references', 'available', 'upon request', 'contact', 'n/a']
    if any(meaningless in job_title.lower() for meaningless in meaningless_titles):
        is_garbage = True
        reasons.append("Meaningless job title")

    # Very short descriptions
    if description and len(description.strip()) < 10:
        is_garbage = True
        reasons.append("Very short description")

    # Check if dates are missing
    start_date = entry.get('StartDate', '')
    end_date = entry.get('EndDate', '')
    if not start_date and not end_date:
        reasons.append("Missing dates (suspicious)")

    if is_garbage:
        garbage_entries.append((i, entry, reasons))

print(f"GARBAGE ENTRIES FOUND ({len(garbage_entries)}):")
for entry_num, entry, reasons in garbage_entries:
    print(f"Entry #{entry_num}: {reasons}")
    print(f"  Job Title: {repr(entry.get('JobTitle', 'N/A'))}")
    print(f"  Company: {repr(entry.get('Employer', 'N/A'))}")
    print()

# Show clean entries
clean_entries = [entry for i, entry in enumerate(work_experience) if (i+1) not in [num for num, _, _ in garbage_entries]]
print(f"=== CLEAN WORK EXPERIENCE ENTRIES ({len(clean_entries)}) ===")
for i, entry in enumerate(clean_entries, 1):
    print(f"{i}. {entry.get('JobTitle', 'N/A')} at {entry.get('Employer', 'N/A')}")
    print(f"   Duration: {entry.get('StartDate', 'N/A')} - {entry.get('EndDate', 'N/A')}")