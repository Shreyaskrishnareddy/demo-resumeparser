from fixed_comprehensive_parser import FixedComprehensiveParser
import json
import fitz

# Debug skills quality for Ahmad Qasem - FIXED VERSION
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

print("=== AHMAD QASEM SKILLS ANALYSIS - FIXED ===")
print(f"Total skills found: {len(skills)}")
print()

# Extract just the skill names for analysis
skill_names = []
for skill in skills:
    if isinstance(skill, dict):
        skill_name = skill.get('SkillName', '')
        skill_names.append(skill_name)
    else:
        skill_names.append(str(skill))

print("=== SKILL NAMES ONLY ===")
for i, skill_name in enumerate(skill_names, 1):
    print(f"{i:2d}. '{skill_name}'")

print()

# Analyze quality issues
print("=== QUALITY ISSUES ANALYSIS ===")

# 1. Find garbage/broken skills
garbage_skills = []
for skill in skill_names:
    # Email addresses
    if '@' in skill:
        garbage_skills.append(f"EMAIL: '{skill}'")
    # Very short/meaningless
    elif len(skill.strip()) < 3:
        garbage_skills.append(f"TOO SHORT: '{skill}'")
    # Single words that don't make sense as skills
    elif skill.strip().lower() in ['issues', 'data', 'news', 'secure', 'to-date', 'updated as needed)', 'reference']:
        garbage_skills.append(f"MEANINGLESS: '{skill}'")
    # Sentence fragments
    elif skill.strip().lower() in ['stakeholders', 'and team members', 'keeping the related team members', 'with a professional technique to']:
        garbage_skills.append(f"FRAGMENT: '{skill}'")
    # Language entries (should not be skills)
    elif 'writing / reading / speaking' in skill.lower():
        garbage_skills.append(f"LANGUAGE: '{skill}'")
    # Generic headers
    elif skill.strip().lower() in ['it skills', 'personal skills']:
        garbage_skills.append(f"HEADER: '{skill}'")
    # References
    elif 'references available' in skill.lower():
        garbage_skills.append(f"REFERENCES: '{skill}'")

print(f"GARBAGE SKILLS FOUND ({len(garbage_skills)}):")
for garbage in garbage_skills:
    print(f"  - {garbage}")

# 2. Find broken skill combinations that should be merged
print(f"\n=== SKILLS THAT SHOULD BE COMBINED ===")

# Find related MS Office skills
ms_office_skills = [skill for skill in skill_names if any(word in skill.lower() for word in ['word', 'excel', 'powerpoint', 'ms office'])]
if len(ms_office_skills) > 1:
    print(f"MS OFFICE SKILLS (should be combined):")
    for skill in ms_office_skills:
        print(f"  - '{skill}'")

# Find SharePoint duplicates
sharepoint_skills = [skill for skill in skill_names if 'sharepoint' in skill.lower()]
if len(sharepoint_skills) > 1:
    print(f"SHAREPOINT SKILLS (should be combined):")
    for skill in sharepoint_skills:
        print(f"  - '{skill}'")

# Find MS Project duplicates
ms_project_skills = [skill for skill in skill_names if 'ms project' in skill.lower()]
if len(ms_project_skills) > 1:
    print(f"MS PROJECT SKILLS (should be combined):")
    for skill in ms_project_skills:
        print(f"  - '{skill}'")

# 3. Extract clean, meaningful skills
clean_skills = []
for skill in skill_names:
    skill_lower = skill.strip().lower()

    # Skip garbage
    is_garbage = any([
        '@' in skill,
        len(skill.strip()) < 3,
        skill_lower in ['issues', 'data', 'news', 'secure', 'to-date', 'updated as needed)', 'reference', 'stakeholders', 'and team members', 'keeping the related team members', 'with a professional technique to'],
        'writing / reading / speaking' in skill_lower,
        skill_lower in ['it skills', 'personal skills'],
        'references available' in skill_lower
    ])

    if not is_garbage:
        clean_skills.append(skill)

print(f"\n=== PROPOSED CLEAN SKILLS ({len(clean_skills)}) ===")
for i, skill in enumerate(clean_skills, 1):
    print(f"{i:2d}. '{skill}'")