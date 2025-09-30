#!/usr/bin/env python3
"""Debug Jumoke's resume parsing directly"""

from fixed_resume_parser import FixedResumeParser
import sys
import fitz

# Extract text from PDF
doc = fitz.open('/home/great/claudeprojects/parser/test_resumes/Test Resumes/Jumoke-Adekanmi-Web-Developer-2025-03-21.pdf')
text = ''
for page in doc:
    text += page.get_text()
doc.close()

print("PDF Text extracted")
print("=" * 50)

# Initialize parser
parser = FixedResumeParser()

# Parse the resume
result = parser.parse_resume(text, "Jumoke-Adekanmi-Web-Developer-2025-03-21.pdf")

# Print results
print("\nPARSING RESULTS:")
print("=" * 50)
print(f"Contact: {result['ContactInformation']['CandidateName']['FormattedName']}")
print(f"Positions found: {len(result['EmploymentHistory']['Positions'])}")

for i, pos in enumerate(result['EmploymentHistory']['Positions']):
    print(f"\nPosition {i+1}:")
    print(f"  Company: {pos['Employer']['Name']}")
    print(f"  Title: {pos['JobTitle']}")
    print(f"  Dates: {pos['Dates']}")
    print(f"  Location: {pos['Location']}")
    print(f"  Description (first 100 chars): {pos['Description'][:100]}...")

print(f"\nTotal experience months: {result['ExperienceMonths']}")
print(f"Skills found: {len(result['Skills'])}")