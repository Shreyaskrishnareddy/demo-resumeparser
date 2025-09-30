from fixed_comprehensive_parser import FixedComprehensiveParser
import fitz

# Test company detection on Ahmad Qasem's specific lines
parser = FixedComprehensiveParser()

# Read PDF text
doc = fitz.open('Resume&Results/Ahmad Qasem-Resume.pdf')
text = ""
for page in doc:
    text += page.get_text()
doc.close()

print("=== TESTING COMPANY DETECTION ON ACTUAL LINES ===")

# Test the specific company lines we found
company_lines = [
    "United Airline – Remote",
    "Emburse – CA",
    "PepsiCo – Chicago, IL",
    "Ligadata Solutions- Menlo Park, CA",
    "EtQ – Tucson, Arizona"
]

for line in company_lines:
    is_company = parser._is_company_dash_location(line)
    print(f"Line: '{line}'")
    print(f"  Is company-location: {is_company}")
    if is_company:
        parsed = parser._parse_company_dash_location(line)
        print(f"  Parsed: Company='{parsed['company']}', Location='{parsed['location']}'")
    print()

# Test job title detection
print("=== TESTING JOB TITLE DETECTION ===")
job_lines = [
    "Project Manager III (July 2021 – Current)",
    "Project Manager (Jan 2021 – Jun 2021)",
    "Project Manager (August 2020 – December 2020)",
    "Project Manager (May 2019 – August 2020)",
    "Project Manager/Coordinator (04/2015 – 11/2018)"
]

for line in job_lines:
    is_job_title = parser._is_job_title_with_dates(line)
    print(f"Line: '{line}'")
    print(f"  Is job title with dates: {is_job_title}")
    if is_job_title:
        parsed = parser._parse_job_title_with_dates(line)
        print(f"  Parsed: Title='{parsed['title']}', Start='{parsed['start_date']}', End='{parsed['end_date']}'")
    print()

# Now test the full experience extraction specifically
print("=== TESTING EXPERIENCE EXTRACTION ===")
experience = parser._extract_experience_fixed(text)
print(f"Total positions extracted: {len(experience)}")
for i, pos in enumerate(experience, 1):
    print(f"{i}. Title: '{pos.get('JobTitle', {}).get('Raw', 'N/A')}'")
    print(f"   Company: '{pos.get('Employer', {}).get('Name', {}).get('Raw', 'N/A')}'")
    print(f"   Start: '{pos.get('StartDate', {}).get('Date', 'N/A')}'")
    print(f"   End: '{pos.get('EndDate', {}).get('Date', 'N/A')}'")
    print()