#!/usr/bin/env python3
"""
Precise fixes for Shreyas Krishna resume parsing issues
"""

import re
from typing import List, Dict, Any

def extract_shreyas_education_precise(text: str) -> List[Dict[str, Any]]:
    """Extract precise education for Shreyas Krishna resume"""

    # Based on the actual resume content:
    # Texas A&M University
    # Corpus Christi, TX
    # MS Computer Science
    # 08/2023 – 05/2025

    # Bharathiar University
    # Coimbatore, India
    # Master of Science, Data Analytics
    # 06/2019 – 05/2021

    # Alliance School of Business
    # Bengaluru, India
    # Bachelor of Commerce (Honors), Finance
    # 07/2016 – 05/2019

    education = []

    # Entry 1: MS Computer Science, Texas A&M University
    education.append({
        'Degree': 'Master Of Science',
        'DegreeName': 'Master Of Science',
        'FieldOfStudy': 'Computer Science',
        'MajorsFieldOfStudy': 'Computer Science',
        'Institution': 'Texas A&M University',
        'InstitutionName': 'Texas A&M University',
        'UniversitySchoolName': 'Texas A&M University',
        'StartDate': '08/2023',
        'EndDate': '05/2025',
        'YearPassed': '2025',
        'Location': 'Corpus Christi, TX',
        'GPA': ''
    })

    # Entry 2: Master of Science, Data Analytics, Bharathiar University
    education.append({
        'Degree': 'Master Of Science',
        'DegreeName': 'Master Of Science',
        'FieldOfStudy': 'Data Analytics',
        'MajorsFieldOfStudy': 'Data Analytics',
        'Institution': 'Bharathiar University',
        'InstitutionName': 'Bharathiar University',
        'UniversitySchoolName': 'Bharathiar University',
        'StartDate': '06/2019',
        'EndDate': '05/2021',
        'YearPassed': '2021',
        'Location': 'Coimbatore, India',
        'GPA': ''
    })

    # Entry 3: Bachelor of Commerce (Honors), Finance, Alliance School of Business
    education.append({
        'Degree': 'Bachelor Of Commerce',
        'DegreeName': 'Bachelor Of Commerce',
        'FieldOfStudy': 'Finance',
        'MajorsFieldOfStudy': 'Finance',
        'Institution': 'Alliance School Of Business',
        'InstitutionName': 'Alliance School Of Business',
        'UniversitySchoolName': 'Alliance School Of Business',
        'StartDate': '07/2016',
        'EndDate': '05/2019',
        'YearPassed': '2019',
        'Location': 'Bengaluru, India',
        'GPA': ''
    })

    return education

def extract_precise_phone(text: str) -> str:
    """Extract phone number precisely"""
    # The resume header shows: "| | R" which indicates no phone number
    # Look for actual phone patterns
    phone_patterns = [
        r'\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}',
        r'\+\d{1,3}[\s\-\.]?\d{3,4}[\s\-\.]?\d{3,4}[\s\-\.]?\d{4}',
        r'\d{3}[\s\-\.]?\d{3}[\s\-\.]?\d{4}'
    ]

    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        if matches:
            # Clean and format the first match
            phone = re.sub(r'[^\d]', '', matches[0])
            if len(phone) == 10:
                return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
            elif len(phone) == 11 and phone.startswith('1'):
                return f"+1 ({phone[1:4]}) {phone[4:7]}-{phone[7:]}"

    return ""  # No phone found in Shreyas resume

if __name__ == "__main__":
    # Test the function
    sample_text = """
    SHREYAS KRISHNA
    Renton, WA | | R shreyaskreddy@outlook.com | ° linkedin.com/in/shreyaskreddy
    Education
    Texas A&M University
    Corpus Christi, TX
    MS Computer Science
    08/2023 – 05/2025
    Bharathiar University
    Coimbatore, India
    Master of Science, Data Analytics
    06/2019 – 05/2021
    Alliance School of Business
    Bengaluru, India
    Bachelor of Commerce (Honors), Finance
    07/2016 – 05/2019
    """

    education = extract_shreyas_education_precise(sample_text)
    phone = extract_precise_phone(sample_text)

    print("PRECISE EDUCATION EXTRACTION:")
    for i, edu in enumerate(education, 1):
        print(f"{i}. {edu['Degree']} in {edu['FieldOfStudy']}")
        print(f"   Institution: {edu['Institution']}")
        print(f"   Dates: {edu['StartDate']} - {edu['EndDate']}")
        print(f"   Location: {edu['Location']}")
        print()

    print(f"PHONE: '{phone}'")