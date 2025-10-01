#!/usr/bin/env python3
"""
Comprehensive test script to validate parser against verification results
"""
import requests
import json
from pathlib import Path
import pandas as pd

# Resume file mappings
RESUMES = {
    "Resume 1": "/home/great/claudeprojects/parser/parserdemo/Resume&Results/Venkat_Rohit_Senior .NET Full Stack Developer (1).docx",
    "Resume 2": "/home/great/claudeprojects/parser/parserdemo/Resume&Results/KrupakarReddy_SystemP.docx",
    "Resume 3": "/home/great/claudeprojects/parser/parserdemo/Resume&Results/ZAMEN_ALADWANI_PROJECT MANAGER_09_01_2023.pdf",
    "Resume 4": "/home/great/claudeprojects/parser/parserdemo/Resume&Results/Ahmad Qasem-Resume.pdf"
}

API_URL = "http://localhost:5000/api/parse"

def parse_resume(file_path):
    """Parse a resume and return the result"""
    try:
        with open(file_path, 'rb') as f:
            file_name = Path(file_path).name
            files = {'file': (file_name, f, 'application/octet-stream')}
            response = requests.post(API_URL, files=files, timeout=120)

        if response.status_code == 200:
            return response.json()
        else:
            return {'success': False, 'error': f"HTTP {response.status_code}"}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def check_field(data, field_name):
    """Check if a field is present and has meaningful value"""
    if not data:
        return False

    # Map field names to JSON paths
    field_mappings = {
        'Full Name': lambda d: bool(d.get('PersonalDetails', {}).get('FullName')),
        'First Name': lambda d: bool(d.get('PersonalDetails', {}).get('FirstName')),
        'Middle Name': lambda d: bool(d.get('PersonalDetails', {}).get('MiddleName')),
        'Last Name': lambda d: bool(d.get('PersonalDetails', {}).get('LastName')),
        'Email ID': lambda d: bool(d.get('PersonalDetails', {}).get('EmailAddress')),
        'Phone Number': lambda d: bool(d.get('PersonalDetails', {}).get('PhoneNumber')),
        'Country Code': lambda d: bool(d.get('PersonalDetails', {}).get('CountryCode')),
        'Social Media Links': lambda d: len(d.get('PersonalDetails', {}).get('SocialMediaLinks', [])) > 0,
        'Current Job Role': lambda d: bool(d.get('OverallSummary', {}).get('CurrentJobRole')),
        'Relevant Job Titles': lambda d: len(d.get('OverallSummary', {}).get('RelevantJobTitles', [])) > 0,
        'Total Experience': lambda d: bool(d.get('OverallSummary', {}).get('TotalExperience')),
        'Summary': lambda d: bool(d.get('OverallSummary', {}).get('OverallSummary')),
        'Job Title': lambda d: any(exp.get('JobTitle') for exp in d.get('ListOfExperiences', [])),
        'Total Experience': lambda d: any(exp.get('ExperienceInYears') for exp in d.get('ListOfExperiences', [])),
        'Summary': lambda d: any(exp.get('Summary') for exp in d.get('ListOfExperiences', [])),
        'Company Name': lambda d: any(exp.get('Employer') for exp in d.get('ListOfExperiences', [])),
        'Employment Type': lambda d: any(exp.get('EmploymentType') for exp in d.get('ListOfExperiences', [])),
        'Location': lambda d: any(exp.get('Location') for exp in d.get('ListOfExperiences', [])),
        'Start Date': lambda d: any(exp.get('StartDate') for exp in d.get('ListOfExperiences', [])),
        'End Date': lambda d: any(exp.get('EndDate') for exp in d.get('ListOfExperiences', [])),
        'Skills Name': lambda d: len(d.get('ListOfSkills', [])) > 0,
        'Skill Experience': lambda d: any(s.get('ExperienceInMonths') for s in d.get('ListOfSkills', [])),
        'Last Used': lambda d: any(s.get('LastUsed') for s in d.get('ListOfSkills', [])),
        'Relevant Skills': lambda d: len(d.get('RelevantSkills', [])) > 0,
        'Full Education Detail': lambda d: len(d.get('Education', [])) > 0,
        'Type of Education': lambda d: any(e.get('DegreeType') for e in d.get('Education', [])),
        'Majors / Field of Study': lambda d: any(e.get('Major') or e.get('FieldOfStudy') for e in d.get('Education', [])),
        'University / School Name': lambda d: any(e.get('Institution') or e.get('School') for e in d.get('Education', [])),
        'Location': lambda d: any(e.get('Location') for e in d.get('Education', [])),
        'Year Passed': lambda d: any(e.get('GraduationYear') or e.get('EndDate') for e in d.get('Education', [])),
        'Certification Name': lambda d: len(d.get('Certifications', [])) > 0,
        'Issuer Name': lambda d: any(c.get('IssuingAuthority') or c.get('Issuer') for c in d.get('Certifications', [])),
        'Issued Year': lambda d: any(c.get('DateIssued') or c.get('IssueDate') for c in d.get('Certifications', [])),
        'Language Name': lambda d: len(d.get('Languages', [])) > 0,
        'Achievements': lambda d: len(d.get('Achievements', [])) > 0,
        'Project Name': lambda d: len(d.get('Projects', [])) > 0,
        'Description of Project': lambda d: any(p.get('Description') for p in d.get('Projects', [])),
        'Company Worked': lambda d: any(p.get('CompanyName') for p in d.get('Projects', [])),
        'Role in Project': lambda d: any(p.get('Role') for p in d.get('Projects', [])),
        'List of Key Responsibilities': lambda d: len(d.get('KeyResponsibilities', [])) > 0,
        'List of Domains': lambda d: bool(d.get('Domain')),
    }

    checker = field_mappings.get(field_name)
    if checker:
        try:
            return checker(data)
        except:
            return False

    return False

def run_comprehensive_test():
    """Run comprehensive test on all resumes"""

    print("=" * 80)
    print("COMPREHENSIVE PARSER VALIDATION TEST")
    print("=" * 80)

    # Load verification data
    excel_path = "/home/great/claudeprojects/parser/parserdemo/Resume&Results/Parser Verification Results  (1).xlsx"
    df = pd.read_excel(excel_path)

    # Parse all resumes
    print("\n📄 Parsing all resumes...")
    parsed_results = {}
    for resume_name, file_path in RESUMES.items():
        print(f"  - Parsing {resume_name}...")
        result = parse_resume(file_path)
        if result.get('success'):
            parsed_results[resume_name] = result.get('data', {})
            # Save individual result
            with open(f"{resume_name.replace(' ', '_')}_result.json", 'w') as f:
                json.dump(result, f, indent=2)
        else:
            print(f"    ❌ Failed: {result.get('error')}")
            parsed_results[resume_name] = None

    print("\n✅ Parsing complete\n")

    # Compare with expected results
    print("=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)

    total_fields = len(df)
    improvements = []
    still_failing = []
    already_working = []

    for idx, row in df.iterrows():
        category = row['Category']
        field_name = row['Data Field']

        for resume_col in ['Resume 1', 'Resume 2', 'Resume 3', 'Resume 4']:
            expected = row[resume_col]
            resume_data = parsed_results.get(resume_col)

            if resume_data is None:
                continue

            actual = check_field(resume_data, field_name)

            # Determine status
            if expected == 'Yes' and actual:
                already_working.append((resume_col, category, field_name))
            elif expected == 'Yes' and not actual:
                still_failing.append((resume_col, category, field_name))
            elif expected == 'No' and actual:
                improvements.append((resume_col, category, field_name))

    # Print summary
    print(f"\n✅ Already Working: {len(already_working)}")
    print(f"🎉 NEW Improvements: {len(improvements)}")
    print(f"❌ Still Failing: {len(still_failing)}")

    # Print improvements
    if improvements:
        print("\n" + "=" * 80)
        print("🎉 IMPROVEMENTS (Previously No, Now Yes)")
        print("=" * 80)
        for resume, category, field in improvements:
            print(f"  ✅ {resume} - {category} - {field}")

    # Print still failing
    if still_failing:
        print("\n" + "=" * 80)
        print("❌ STILL FAILING (Expected Yes, Got No)")
        print("=" * 80)
        for resume, category, field in still_failing:
            print(f"  ❌ {resume} - {category} - {field}")

    # Calculate improvement percentage
    total_tests = len(already_working) + len(improvements) + len(still_failing)
    if total_tests > 0:
        success_rate = (len(already_working) + len(improvements)) / total_tests * 100
        improvement_rate = len(improvements) / total_tests * 100
        print("\n" + "=" * 80)
        print(f"📊 OVERALL SUCCESS RATE: {success_rate:.1f}%")
        print(f"📈 IMPROVEMENT RATE: {improvement_rate:.1f}%")
        print("=" * 80)

    # Save detailed report
    report = {
        'total_tests': total_tests,
        'already_working': len(already_working),
        'improvements': len(improvements),
        'still_failing': len(still_failing),
        'success_rate': f"{success_rate:.1f}%",
        'improvement_rate': f"{improvement_rate:.1f}%",
        'improvements_detail': [{'resume': r, 'category': c, 'field': f} for r, c, f in improvements],
        'failures_detail': [{'resume': r, 'category': c, 'field': f} for r, c, f in still_failing]
    }

    with open('validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print("\n📄 Detailed report saved to: validation_report.json")
    print("📄 Individual resume results saved as: Resume_*_result.json")

if __name__ == '__main__':
    run_comprehensive_test()
