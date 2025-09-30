import openpyxl
from fixed_comprehensive_parser import FixedComprehensiveParser
from docx import Document
import json

# Analyze the verification Excel to find ALL issues
print("="*80)
print("📋 KRUPAKAR REDDY - DETAILED VERIFICATION ANALYSIS")
print("="*80)

# Load verification Excel
wb = openpyxl.load_workbook('Resume&Results/Resume 3 - Krupakar Reddy P (1).xlsx')
sheet = wb.active

# Parse the resume
doc = Document('Resume&Results/KrupakarReddy_SystemP.docx')
text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
parser = FixedComprehensiveParser()
result = parser.parse_resume(text, 'KrupakarReddy_SystemP.docx')

print("\n📊 VERIFICATION DATA ANALYSIS:")
print("="*80)

issues = []
row_num = 1

for row in sheet.iter_rows(values_only=True):
    row_num += 1
    if row_num == 1:  # Skip header
        continue

    if row[0] is None:  # Skip empty rows
        continue

    s_no = row[0]
    category = row[1]
    data_field = row[2]
    json_present = row[3]
    expected_value = row[4]
    json_component = row[5]
    comments = row[6]

    # Check for issues (json_present == "No" or issues in comments)
    if json_present and str(json_present).strip().upper() == "NO":
        issues.append({
            'row': row_num,
            'category': category,
            'field': data_field,
            'expected': expected_value,
            'component': json_component,
            'comment': comments,
            'severity': 'MISSING'
        })
    elif json_present and str(json_present).strip().upper() == "YES":
        # Check if there are quality issues mentioned in comments
        if comments and any(word in str(comments).lower() for word in ['wrong', 'issue', 'incorrect', 'misclassified', 'duplicate']):
            issues.append({
                'row': row_num,
                'category': category,
                'field': data_field,
                'expected': expected_value,
                'component': json_component,
                'comment': comments,
                'severity': 'QUALITY_ISSUE'
            })

# Group issues by category
issues_by_category = {}
for issue in issues:
    cat = issue['category']
    if cat not in issues_by_category:
        issues_by_category[cat] = []
    issues_by_category[cat].append(issue)

print(f"\n📋 TOTAL ISSUES FOUND: {len(issues)}")
print(f"📂 CATEGORIES WITH ISSUES: {len(issues_by_category)}")
print()

# Show issues by category
for category, cat_issues in sorted(issues_by_category.items()):
    print(f"\n{'='*80}")
    print(f"📁 {category.upper()}")
    print(f"{'='*80}")
    print(f"Issues: {len(cat_issues)}")

    for issue in cat_issues:
        severity_icon = "❌" if issue['severity'] == 'MISSING' else "⚠️"
        print(f"\n{severity_icon} {issue['field']}")
        print(f"   Expected: {issue['expected']}")
        print(f"   Component: {issue['component']}")
        if issue['comment']:
            print(f"   Comment: {issue['comment']}")

# Now check what we actually extracted vs what's expected
print(f"\n\n{'='*80}")
print("🔍 ACTUAL VS EXPECTED COMPARISON")
print(f"{'='*80}")

# Personal Details
print("\n👤 PERSONAL DETAILS:")
personal = result.get('PersonalDetails', {})
print(f"   Full Name: '{personal.get('FullName', 'MISSING')}'")
print(f"   Email: '{personal.get('EmailID', 'MISSING')}'")
print(f"   Phone: '{personal.get('PhoneNumber', 'MISSING')}'")

# Work Experience
print("\n💼 WORK EXPERIENCE:")
work_exp = result.get('ListOfExperiences', [])
print(f"   Total positions: {len(work_exp)}")
for i, exp in enumerate(work_exp, 1):
    print(f"   {i}. {exp.get('JobTitle', 'N/A')} at {exp.get('CompanyName', 'N/A')}")
    print(f"      Start: {exp.get('StartDate', 'N/A')}, End: {exp.get('EndDate', 'N/A')}")

# Skills
print("\n🛠️ SKILLS:")
skills = result.get('ListOfSkills', [])
print(f"   Total skills: {len(skills)}")
skill_names = [s.get('SkillName', '') for s in skills]
print(f"   First 10: {', '.join(skill_names[:10])}")

# Education
print("\n🎓 EDUCATION:")
education = result.get('Education', [])
if education:
    print(f"   Total entries: {len(education)}")
    for i, edu in enumerate(education, 1):
        print(f"   {i}. {edu.get('Degree', 'N/A')} from {edu.get('Institution', 'N/A')}")
else:
    print("   ❌ No education entries found")

# Languages
print("\n🌐 LANGUAGES:")
languages = result.get('Languages', [])
if languages:
    print(f"   Total: {len(languages)}")
    for lang in languages:
        print(f"   - {lang.get('Language', 'N/A')}: {lang.get('Proficiency', 'N/A')}")
else:
    print("   ❌ No languages found")

# Certifications
print("\n📜 CERTIFICATIONS:")
certifications = result.get('Certifications', [])
if certifications:
    print(f"   Total: {len(certifications)}")
    for cert in certifications:
        print(f"   - {cert.get('Name', 'N/A')}")
else:
    print("   ❌ No certifications found")

print("\n" + "="*80)
print("📝 SUMMARY:")
print("="*80)
print(f"Total verification issues: {len(issues)}")
print(f"Categories affected: {len(issues_by_category)}")
print(f"\nMost critical issues:")
print(f"  - Overall Summary fields (Current Job Role, Total Experience, Summary)")
print(f"  - Work Experience details (may need better extraction)")
print(f"  - Education (not present in resume)")
print(f"  - Certifications (not present in resume)")
print(f"  - Projects (not present in resume)")
print("="*80)