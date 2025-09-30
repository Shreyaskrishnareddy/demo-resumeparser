from fixed_comprehensive_parser import FixedComprehensiveParser
import json
import fitz

# Debug skills quality for Ahmad Qasem
parser = FixedComprehensiveParser()

# Read PDF text
doc = fitz.open('Resume&Results/Ahmad Qasem-Resume.pdf')
text = ""
for page in doc:
    text += page.get_text()
doc.close()

# Parse full resume to get skills
result = parser.parse_resume(text, 'Ahmad Qasem-Resume.pdf')
skills = result.get('ListOfSkills', [])

print("=== AHMAD QASEM SKILLS ANALYSIS ===")
print(f"Total skills found: {len(skills)}")
print()

# Analyze each skill
print("=== ALL SKILLS FOUND ===")
for i, skill in enumerate(skills, 1):
    print(f"{i:2d}. {repr(skill)}")

print()

# Analyze skill types and quality issues
skill_texts = []
if isinstance(skills[0], dict) if skills else False:
    # If skills are objects, extract the name/text field
    for skill in skills:
        skill_text = skill.get('Name', skill.get('Skill', skill.get('Text', str(skill))))
        skill_texts.append(skill_text)
else:
    # If skills are just strings
    skill_texts = [str(skill) for skill in skills]

print("=== SKILL TEXTS FOR QUALITY ANALYSIS ===")
for i, skill_text in enumerate(skill_texts, 1):
    print(f"{i:2d}. '{skill_text}'")

print()

# Look for quality issues
print("=== QUALITY ISSUES ANALYSIS ===")

# Find duplicates
seen = set()
duplicates = []
for skill in skill_texts:
    skill_lower = skill.lower().strip()
    if skill_lower in seen:
        duplicates.append(skill)
    seen.add(skill_lower)

if duplicates:
    print(f"DUPLICATES FOUND ({len(duplicates)}):")
    for dup in duplicates:
        print(f"  - '{dup}'")
else:
    print("No exact duplicates found")

# Find very short skills (likely broken)
short_skills = [skill for skill in skill_texts if len(skill.strip()) < 3]
if short_skills:
    print(f"\nVERY SHORT SKILLS ({len(short_skills)}):")
    for skill in short_skills:
        print(f"  - '{skill}'")

# Find very long skills (likely concatenated)
long_skills = [skill for skill in skill_texts if len(skill.strip()) > 50]
if long_skills:
    print(f"\nVERY LONG SKILLS ({len(long_skills)}):")
    for skill in long_skills:
        print(f"  - '{skill[:50]}...'")

# Find non-alphanumeric heavy skills (likely broken)
import re
weird_skills = [skill for skill in skill_texts if len(re.sub(r'[a-zA-Z0-9\s\-\+\.\#]', '', skill)) > len(skill) * 0.3]
if weird_skills:
    print(f"\nWEIRD CHARACTER SKILLS ({len(weird_skills)}):")
    for skill in weird_skills:
        print(f"  - '{skill}'")