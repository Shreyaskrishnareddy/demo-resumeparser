import fitz

# Check actual work experience content in Ahmad Qasem's PDF
doc = fitz.open('Resume&Results/Ahmad Qasem-Resume.pdf')
text = ""
for page in doc:
    text += page.get_text()
doc.close()

print("=== SEARCHING FOR WORK EXPERIENCE SECTION ===")

lines = text.split('\n')

# Find lines that mention experience-related keywords
experience_keywords = ['experience', 'employment', 'work', 'project manager', 'manager']

print("Lines mentioning work experience:")
for i, line in enumerate(lines):
    line_lower = line.lower()
    if any(keyword in line_lower for keyword in experience_keywords):
        print(f"Line {i}: {repr(line.strip())}")

print(f"\n=== LOOKING FOR COMPANY NAMES ===")

# Look for potential company name patterns around project manager entries
for i, line in enumerate(lines):
    if 'project manager' in line.lower():
        # Show context around this line
        start_idx = max(0, i-3)
        end_idx = min(len(lines), i+4)
        print(f"\n--- Context around line {i}: '{line.strip()}' ---")
        for j in range(start_idx, end_idx):
            marker = ">>>" if j == i else "   "
            print(f"{marker} {j:3d}: {repr(lines[j].strip())}")

# Also look for common company name patterns
print(f"\n=== LOOKING FOR COMPANY NAME PATTERNS ===")
import re

# Common company patterns
company_patterns = [
    r'\b[A-Z][a-zA-Z\s&]+(?:Inc|LLC|Corp|Company|Group|Solutions|Systems|Technologies|Services)\b',
    r'\b[A-Z][a-zA-Z\s&]{3,20}\b(?=\s*[-–]|\s*\n|\s*\|)',  # Capitalized names followed by separators
]

for pattern in company_patterns:
    matches = re.findall(pattern, text)
    if matches:
        print(f"Pattern matches: {matches}")

# Look for lines with dates that might indicate work experience
date_pattern = r'\b(?:0[1-9]|1[0-2])/\d{4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b|\b\d{1,2}\s+\d{4}\b'
print(f"\n=== LINES WITH DATES ===")
for i, line in enumerate(lines):
    if re.search(date_pattern, line):
        print(f"Line {i}: {repr(line.strip())}")