from fixed_comprehensive_parser import FixedComprehensiveParser
import fitz
import json

# Comprehensive analysis of Krupakar Reddy resume
parser = FixedComprehensiveParser()

# Read DOCX file
resume_path = 'Resume&Results/KrupakarReddy_SystemP.docx'

# Since it's a DOCX, we need to extract text first
try:
    from docx import Document
    doc = Document(resume_path)
    text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    print(f"✅ Successfully extracted {len(text)} characters from DOCX")
except Exception as e:
    print(f"❌ Error reading DOCX: {e}")
    exit(1)

# Parse the resume
result = parser.parse_resume(text, 'KrupakarReddy_SystemP.docx')

print("\n" + "="*80)
print("🔍 KRUPAKAR REDDY - COMPREHENSIVE ANALYSIS")
print("="*80)

# Analyze each section
sections = {
    'Education': result.get('Education', []),
    'Languages': result.get('Languages', []),
    'ListOfSkills': result.get('ListOfSkills', []),
    'ListOfExperiences': result.get('ListOfExperiences', []),
    'Certifications': result.get('Certifications', []),
    'PersonalDetails': result.get('PersonalDetails', {})
}

print(f"\n📊 SECTION SUMMARY:")
print(f"   Education: {len(sections['Education'])} entries")
print(f"   Languages: {len(sections['Languages'])} entries")
print(f"   Skills: {len(sections['ListOfSkills'])} entries")
print(f"   Work Experience: {len(sections['ListOfExperiences'])} entries")
print(f"   Certifications: {len(sections['Certifications'])} entries")

# Detailed Education Analysis
print(f"\n🎓 EDUCATION ANALYSIS:")
if sections['Education']:
    for i, edu in enumerate(sections['Education'], 1):
        print(f"\n   Entry {i}:")
        print(f"      Degree: {repr(edu.get('Degree', 'MISSING'))}")
        print(f"      Major: {repr(edu.get('Major', 'MISSING'))}")
        print(f"      FieldOfStudy: {repr(edu.get('FieldOfStudy', 'MISSING'))}")
        print(f"      Institution: {repr(edu.get('Institution', 'MISSING'))}")
        print(f"      Year: {repr(edu.get('GraduationYear', 'MISSING'))}")

        # Check for issues
        issues = []
        if not edu.get('Major'):
            issues.append("Missing Major")
        if not edu.get('FieldOfStudy'):
            issues.append("Missing FieldOfStudy")
        if not edu.get('Institution'):
            issues.append("Missing Institution")
        if not edu.get('GraduationYear'):
            issues.append("Missing Year")

        if issues:
            print(f"      ⚠️  ISSUES: {', '.join(issues)}")
        else:
            print(f"      ✅ Complete")
else:
    print("   ❌ NO EDUCATION ENTRIES FOUND")

# Languages Analysis
print(f"\n🌐 LANGUAGES ANALYSIS:")
if sections['Languages']:
    for i, lang in enumerate(sections['Languages'], 1):
        print(f"   {i}. {lang.get('Language', 'UNKNOWN')}: {lang.get('Proficiency', 'N/A')}")
else:
    print("   ❌ NO LANGUAGES FOUND")

# Skills Analysis
print(f"\n🛠️ SKILLS ANALYSIS:")
if sections['ListOfSkills']:
    print(f"   Total: {len(sections['ListOfSkills'])} skills")

    # Check for garbage
    skill_names = [s.get('SkillName', '') for s in sections['ListOfSkills']]
    garbage_count = 0

    for skill in skill_names:
        if '@' in skill or len(skill) < 3 or skill.lower() in ['data', 'news', 'issues']:
            garbage_count += 1

    print(f"   Clean skills: {len(sections['ListOfSkills']) - garbage_count}")
    print(f"   Garbage/issues: {garbage_count}")

    # Show first 10 skills
    print(f"\n   First 10 skills:")
    for i, skill in enumerate(skill_names[:10], 1):
        print(f"      {i}. {repr(skill)}")
else:
    print("   ❌ NO SKILLS FOUND")

# Work Experience Analysis
print(f"\n💼 WORK EXPERIENCE ANALYSIS:")
if sections['ListOfExperiences']:
    print(f"   Total: {len(sections['ListOfExperiences'])} positions")

    for i, exp in enumerate(sections['ListOfExperiences'], 1):
        title = exp.get('JobTitle', 'N/A')
        company = exp.get('Employer', 'N/A')

        print(f"\n   Position {i}:")
        print(f"      Title: {repr(title)}")
        print(f"      Company: {repr(company)}")

        # Check for issues
        if company == 'N/A' or not company:
            print(f"      ⚠️  ISSUE: Missing company name")
        if title == 'N/A' or not title:
            print(f"      ⚠️  ISSUE: Missing job title")
else:
    print("   ❌ NO WORK EXPERIENCE FOUND")

# Certifications Analysis
print(f"\n📜 CERTIFICATIONS ANALYSIS:")
if sections['Certifications']:
    print(f"   Total: {len(sections['Certifications'])} certifications")

    # Check for duplicates
    cert_names = [c.get('Name', '') for c in sections['Certifications']]
    unique_certs = set([c.lower() for c in cert_names if c])

    print(f"   Unique: {len(unique_certs)}")
    if len(cert_names) != len(unique_certs):
        print(f"   ⚠️  DUPLICATES: {len(cert_names) - len(unique_certs)} duplicate entries")

    print(f"\n   Certifications list:")
    for i, cert in enumerate(cert_names, 1):
        print(f"      {i}. {repr(cert)}")
else:
    print("   ❌ NO CERTIFICATIONS FOUND")

# Personal Details
print(f"\n👤 PERSONAL DETAILS:")
pd = sections['PersonalDetails']
print(f"   Name: {repr(pd.get('FullName', 'MISSING'))}")
print(f"   Email: {repr(pd.get('EmailID', 'MISSING'))}")
print(f"   Phone: {repr(pd.get('PhoneNumber', 'MISSING'))}")

# Processing metadata
metadata = result.get('ParsingMetadata', {})
print(f"\n⚙️ PARSING METADATA:")
print(f"   Processing Time: {metadata.get('processing_time', 0):.3f}s")
print(f"   Accuracy Score: {metadata.get('accuracy_score', 0)}")

print("\n" + "="*80)
print("📋 SUMMARY OF ISSUES TO FIX:")
print("="*80)

# Collect all issues
all_issues = []

if not sections['Education']:
    all_issues.append("❌ CRITICAL: No education entries found")
elif any(not e.get('Major') or not e.get('FieldOfStudy') for e in sections['Education']):
    all_issues.append("⚠️  Education missing Major/FieldOfStudy")

if not sections['Languages']:
    all_issues.append("❌ CRITICAL: No languages found")

if garbage_count > 0:
    all_issues.append(f"⚠️  Skills have {garbage_count} garbage entries")

if not sections['ListOfExperiences']:
    all_issues.append("❌ CRITICAL: No work experience found")

if sections['Certifications'] and len(cert_names) != len(unique_certs):
    all_issues.append(f"⚠️  Certifications have {len(cert_names) - len(unique_certs)} duplicates")

if all_issues:
    for issue in all_issues:
        print(f"   {issue}")
else:
    print("   ✅ No major issues found!")

print("\n" + "="*80)