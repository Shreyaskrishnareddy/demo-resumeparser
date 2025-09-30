from fixed_comprehensive_parser import FixedComprehensiveParser
import fitz  # PyMuPDF

# Debug language extraction for Ahmad Qasem
resume_path = 'Resume&Results/Ahmad Qasem-Resume.pdf'

# Read PDF
doc = fitz.open(resume_path)
text = ""
for page in doc:
    text += page.get_text()
doc.close()

parser = FixedComprehensiveParser()

print("=== AHMAD QASEM LANGUAGE ANALYSIS ===")

# Test language extraction
languages = parser._extract_languages_comprehensive(text)
print(f"Current language extraction result: {languages}")
print(f"Number of languages found: {len(languages)}")

# Look for language-related sections in the text
lines = text.split('\n')
print(f"\n=== LOOKING FOR LANGUAGE KEYWORDS ===")
language_keywords = ['language', 'languages', 'arabic', 'english', 'fluent', 'native', 'beginner', 'intermediate', 'advanced']

for i, line in enumerate(lines):
    line_lower = line.lower()
    if any(keyword in line_lower for keyword in language_keywords):
        print(f"Line {i}: {repr(line.strip())}")

# Also check for lines that might contain language information
print(f"\n=== FULL TEXT SEARCH FOR LANGUAGE PATTERNS ===")
import re

# Look for common language patterns
patterns = [
    r'\b(?:fluent|native|beginner|intermediate|advanced|basic)\s+(?:in\s+)?(?:arabic|english|french|spanish|german|italian|chinese|japanese|korean|russian)\b',
    r'\b(?:arabic|english|french|spanish|german|italian|chinese|japanese|korean|russian)[\s:-]*(?:fluent|native|beginner|intermediate|advanced|basic)?\b',
    r'languages?[\s:]*[\w\s,]+',
]

for i, pattern in enumerate(patterns, 1):
    matches = re.findall(pattern, text, re.IGNORECASE)
    if matches:
        print(f"Pattern {i} matches: {matches}")

# Let's also look at the verification data to see what languages should be extracted
print(f"\n=== CHECKING EXPECTED LANGUAGES FROM VERIFICATION DATA ===")
# Expected from the verification analysis: English (native) and Arabic (native)