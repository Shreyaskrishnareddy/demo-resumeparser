#!/usr/bin/env python3
"""
Comprehensive field-by-field validation against original Excel verification results
"""

import pandas as pd
import json
import time
from pathlib import Path
from fixed_comprehensive_parser import FixedComprehensiveParser
import fitz  # PyMuPDF

def extract_text_from_file(file_path):
    """Extract text from PDF/DOC/DOCX files"""
    try:
        if file_path.endswith('.pdf'):
            doc = fitz.open(file_path)
            text = ''
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        # Add DOC/DOCX support if needed
        return ""
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ""

def validate_field(parsed_data, field_category, field_name, resume_num):
    """Validate a specific field from parsed data"""
    try:
        if field_category == "Personal Details":
            personal_details = parsed_data.get('PersonalDetails', {})

            if field_name == "Full Name":
                full_name = personal_details.get('FullName', '')
                return bool(full_name and full_name.strip() and full_name != 'N/A')

            elif field_name == "First Name":
                first_name = personal_details.get('FirstName', '')
                return bool(first_name and first_name.strip() and first_name != 'N/A')

            elif field_name == "Middle Name":
                middle_name = personal_details.get('MiddleName', '')
                return bool(middle_name and middle_name.strip())

            elif field_name == "Last Name":
                last_name = personal_details.get('LastName', '')
                return bool(last_name and last_name.strip() and last_name != 'N/A')

            elif field_name == "Email ID":
                email = personal_details.get('EmailID', '')
                return bool(email and email.strip() and email != 'N/A')

            elif field_name == "Phone Number":
                phone = personal_details.get('PhoneNumber', '')
                return bool(phone and phone.strip() and phone != 'N/A')

            elif field_name == "Country Code":
                country_code = personal_details.get('CountryCode', '')
                return bool(country_code and country_code.strip())

            elif field_name == "Social Media Links":
                social_media = parsed_data.get('SocialMedia', [])
                return bool(social_media)

        elif field_category == "Overall Summary":
            overall_summary = parsed_data.get('OverallSummary', {})

            if field_name == "Current Job Role":
                # Check if there's a current position in work experience
                experience_list = parsed_data.get('ListOfExperiences', [])
                current_positions = [exp for exp in experience_list if exp.get('EndDate', '') == 'Current']
                return bool(current_positions)

            elif field_name == "Relevant Job Titles":
                relevant_jobs = overall_summary.get('RelevantJobTitles', [])
                return bool(relevant_jobs)

            elif field_name == "Total Experience":
                total_exp = overall_summary.get('TotalExperience', '')
                return bool(total_exp and total_exp.strip() and total_exp != '0 years')

            elif field_name == "Summary":
                summary_data = overall_summary.get('OverallSummary', {})
                summary_text = summary_data.get('Text', '')
                return bool(summary_text and summary_text.strip())

        elif field_category == "Work Experiences":
            experience_list = parsed_data.get('ListOfExperiences', [])

            if field_name == "Job Title":
                return bool(any(exp.get('JobTitle') for exp in experience_list))

            elif field_name == "Total Experience":
                return bool(any(exp.get('ExperienceInYears') for exp in experience_list))

            elif field_name == "Summary":
                return bool(any(exp.get('Summary') for exp in experience_list))

            elif field_name == "Company Name":
                return bool(any(exp.get('CompanyName') for exp in experience_list))

            elif field_name == "Employment Type":
                return bool(any(exp.get('EmploymentType') for exp in experience_list))

            elif field_name == "Location":
                return bool(any(exp.get('Location') for exp in experience_list))

            elif field_name == "Start Date":
                return bool(any(exp.get('StartDate') for exp in experience_list))

            elif field_name == "End Date":
                return bool(any(exp.get('EndDate') for exp in experience_list))

        elif field_category == "Skills":
            skills_list = parsed_data.get('ListOfSkills', [])

            if field_name == "Skills Name":
                return bool(any(skill.get('SkillName') for skill in skills_list))

            elif field_name == "Skill Experience":
                return bool(any(skill.get('ExperienceInMonths') for skill in skills_list))

            elif field_name == "Last Used":
                return bool(any(skill.get('LastUsed') for skill in skills_list))

            elif field_name == "Relevant Skills":
                # Check if skills are properly categorized
                return bool(any(skill.get('Type') for skill in skills_list))

        elif field_category == "Education":
            education_list = parsed_data.get('Education', [])

            if field_name == "Full Education Detail":
                return bool(education_list)

            elif field_name == "Type of Education":
                return bool(any(edu.get('DegreeType') or edu.get('Degree') for edu in education_list))

            elif field_name == "Majors / Field of Study":
                return bool(any(edu.get('Major') or edu.get('FieldOfStudy') for edu in education_list))

            elif field_name == "University / School Name":
                return bool(any(edu.get('Institution') or edu.get('School') for edu in education_list))

            elif field_name == "Location":
                return bool(any(edu.get('Location') for edu in education_list))

            elif field_name == "Year Passed":
                return bool(any(edu.get('GraduationYear') or edu.get('EndDate') for edu in education_list))

        elif field_category == "Certifications":
            cert_list = parsed_data.get('Certifications', [])

            if field_name == "Certification Name":
                return bool(any(cert.get('CertificationName') or cert.get('Name') for cert in cert_list))

            elif field_name == "Issuer Name":
                return bool(any(cert.get('IssuingAuthority') or cert.get('Issuer') for cert in cert_list))

            elif field_name == "Issued Year":
                return bool(any(cert.get('IssueDate') or cert.get('Date') for cert in cert_list))

        elif field_category == "Languages":
            languages = parsed_data.get('Languages', [])

            if field_name == "Language Name":
                return bool(any(lang.get('Language') or lang.get('Name') for lang in languages))

        elif field_category == "Achievements":
            achievements = parsed_data.get('Achievements', [])
            return bool(achievements)

        elif field_category == "Projects":
            projects = parsed_data.get('Projects', [])

            if field_name == "Project Name":
                return bool(any(proj.get('ProjectName') or proj.get('Name') for proj in projects))

            elif field_name == "Description of Project":
                return bool(any(proj.get('Description') for proj in projects))

            elif field_name == "Company Worked":
                return bool(any(proj.get('Client') or proj.get('Company') for proj in projects))

            elif field_name == "Role in Project":
                return bool(any(proj.get('Role') for proj in projects))

            elif field_name == "Start Date":
                return bool(any(proj.get('StartDate') for proj in projects))

            elif field_name == "End Date":
                return bool(any(proj.get('EndDate') for proj in projects))

        elif field_category == "Key Responsibilities":
            if field_name == "List of Key Responsibilities":
                experience_list = parsed_data.get('ListOfExperiences', [])
                return bool(any(exp.get('Summary') or exp.get('Description') for exp in experience_list))

        elif field_category == "Domain":
            if field_name == "List of Domains":
                # Check if domain/industry information is extracted
                return False  # Not implemented in current parser

        return False

    except Exception as e:
        print(f"Error validating {field_category} - {field_name} for Resume {resume_num}: {e}")
        return False

def main():
    # Resume file paths
    resume_files = {
        1: "/home/great/claudeprojects/parser/test_resumes/Test Resumes/Ahmad Qasem-Resume.pdf",
        2: "/home/great/claudeprojects/parser/test_resumes/Test Resumes/ZAMEN_ALADWANI_PROJECT MANAGER_09_01_2023.pdf",
        3: "/home/great/claudeprojects/parser/test_resumes/Test Resumes/PRANAY REDDY_DE_Resume.pdf",
        4: "/home/great/claudeprojects/parser/test_resumes/Test Resumes/Mahesh_Bolikonda (1).pdf"
    }

    # Load original verification results
    excel_file = 'Resume&Results/Parser Verification Results .xlsx'
    original_df = pd.read_excel(excel_file, sheet_name='Sheet1')

    # Initialize parser
    parser = FixedComprehensiveParser()

    # Parse all resumes
    print("🔍 Parsing all resumes with current fixed parser...")
    parsed_results = {}

    for resume_num, file_path in resume_files.items():
        print(f"   Parsing Resume {resume_num}...")
        text = extract_text_from_file(file_path)
        if text:
            try:
                result = parser.parse_resume(text)
                parsed_results[resume_num] = result
                print(f"   ✅ Resume {resume_num} parsed successfully")
            except Exception as e:
                print(f"   ❌ Resume {resume_num} failed: {e}")
                parsed_results[resume_num] = {}
        else:
            print(f"   ❌ Resume {resume_num} - failed to extract text")
            parsed_results[resume_num] = {}

    print("\n" + "="*100)
    print("📊 COMPREHENSIVE FIELD-BY-FIELD VALIDATION RESULTS")
    print("="*100)

    # Track improvements
    improvements = {"fixed": 0, "still_missing": 0, "total_issues": 0}
    resume_improvements = {1: {"fixed": 0, "total": 0}, 2: {"fixed": 0, "total": 0},
                          3: {"fixed": 0, "total": 0}, 4: {"fixed": 0, "total": 0}}

    # Validate each field
    for index, row in original_df.iterrows():
        field_num = row['S. No.']
        category = row['Category']
        field_name = row['Data Field']

        print(f"\n{field_num:2d}. {category} - {field_name}")
        print("    " + "-" * 80)

        for resume_num in range(1, 5):
            original_status = row[f'Resume {resume_num}']
            original_working = (original_status == 'Yes')

            # Validate current parser output
            current_working = False
            if resume_num in parsed_results:
                current_working = validate_field(parsed_results[resume_num], category, field_name, resume_num)

            # Determine status
            if original_working and current_working:
                status = "✅ MAINTAINED"
                status_color = ""
            elif not original_working and current_working:
                status = "🎯 FIXED"
                status_color = ""
                improvements["fixed"] += 1
                resume_improvements[resume_num]["fixed"] += 1
            elif original_working and not current_working:
                status = "❌ REGRESSED"
                status_color = ""
            else:
                status = "⚠️  STILL MISSING"
                status_color = ""
                improvements["still_missing"] += 1

            if not original_working:
                improvements["total_issues"] += 1
                resume_improvements[resume_num]["total"] += 1

            print(f"    Resume {resume_num}: {original_status:>3} → {'Yes' if current_working else 'No':>3} | {status}")

        # Show observations from original
        observations = row['Observations / Issues']
        if pd.notna(observations):
            print(f"    Original Issue: {observations}")

    print("\n" + "="*100)
    print("📈 IMPROVEMENT SUMMARY")
    print("="*100)

    # Overall improvements
    total_original_issues = improvements["total_issues"]
    total_fixed = improvements["fixed"]
    still_missing = improvements["still_missing"]

    fix_rate = (total_fixed / total_original_issues * 100) if total_original_issues > 0 else 0

    print(f"📊 Overall Field-Level Improvements:")
    print(f"   Total Original Issues: {total_original_issues}")
    print(f"   Issues Fixed: {total_fixed}")
    print(f"   Still Missing: {still_missing}")
    print(f"   Fix Rate: {fix_rate:.1f}%")

    print(f"\n📋 Resume-by-Resume Improvements:")
    for resume_num in range(1, 5):
        resume_fixed = resume_improvements[resume_num]["fixed"]
        resume_total = resume_improvements[resume_num]["total"]
        resume_rate = (resume_fixed / resume_total * 100) if resume_total > 0 else 0
        print(f"   Resume {resume_num}: {resume_fixed}/{resume_total} fields fixed ({resume_rate:.1f}%)")

    # Save detailed results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"comprehensive_field_validation_results_{timestamp}.json"

    detailed_results = {
        "timestamp": timestamp,
        "parser_version": "Fixed-Comprehensive-v2.0",
        "total_fields_tested": len(original_df),
        "improvements": improvements,
        "resume_improvements": resume_improvements,
        "fix_rate_percentage": fix_rate,
        "parsed_results_sample": {str(k): v for k, v in list(parsed_results.items())[:1]}  # Sample for size
    }

    with open(results_file, 'w') as f:
        json.dump(detailed_results, f, indent=2, default=str)

    print(f"\n📄 Detailed results saved to: {results_file}")
    print("\n🎯 Field-by-field validation completed!")

if __name__ == "__main__":
    main()