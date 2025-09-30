#!/usr/bin/env python3
"""
Comprehensive Resume Parser - Addresses all critical missing field issues
Fixes: job titles, middle names, social media, education details, projects, etc.
"""

import re
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveResumeParser:
    """
    Comprehensive resume parser addressing all identified issues:
    - Missing job titles in work experience
    - Missing middle names
    - Missing social media links
    - Missing education school names
    - Missing professional summary
    - Missing projects extraction
    - Improved skills categorization
    """

    def __init__(self):
        self._init_patterns()
        logger.info("Comprehensive Resume Parser initialized - v1.0")

    def _init_patterns(self):
        """Initialize comprehensive patterns"""

        # Enhanced email patterns
        self.email_patterns = [
            r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
        ]

        # Enhanced phone patterns (same as before but improved)
        self.phone_patterns = [
            r'\((\d{3})\)[-.–\s]*(\d{3})[-.–\s]*(\d{4})',
            r'\((\d{3})\)\s*(\d{3})[-.–]\s*(\d{4})',
            r'(\d{3})[-.–\s]+(\d{3})[-.–\s]+(\d{4})',
            r'\+1?\s*(\d{3})[-.–)\s]*(\d{3})[-.–)\s]*(\d{4})',
            r'Phone[:\s]*\(?(\d{3})\)?[-.–\s]*(\d{3})[-.–\s]*(\d{4})',
            r'Tel[:\s]*\(?(\d{3})\)?[-.–\s]*(\d{3})[-.–\s]*(\d{4})',
            r'Mobile[:\s]*\(?(\d{3})\)?[-.–\s]*(\d{3})[-.–\s]*(\d{4})',
            r'Cell[:\s]*\(?(\d{3})\)?[-.–\s]*(\d{3})[-.–\s]*(\d{4})',
            r'[A-Za-z\s,]+\s+(\d{3})[-.–\s]*(\d{3})[-.–\s]*(\d{4})\s*$',
            r'[0-9]{5}\s+(\d{3})[-.–\s]*(\d{3})[-.–\s]*(\d{4})',
            r'FL\s*(\d{3})\s*(\d{3})[-.–\s]*(\d{4})',
            r'Email:\s*[^@\s]+@[^@\s]+\.[a-z]+\s+(\d{3})[-.–\s]*(\d{3})[-.–\s]*(\d{4})',
            r'(?:PO Box|Box|Address|Contact)[^0-9]*(\d{3})[-.–\s]*(\d{3})[-.–\s]*(\d{4})',
            r'(?<!\d)(\d{3})[-.–\s]{0,3}(\d{3})[-.–\s]{0,3}(\d{4})(?!\d)',
        ]

        # Social media patterns
        self.social_media_patterns = [
            r'(?:linkedin\.com/in/|linkedin\.com/pub/|linkedin\.com/profile/view\?id=)([a-zA-Z0-9\-\.]+)',
            r'(?:github\.com/)([a-zA-Z0-9\-\.]+)',
            r'(?:twitter\.com/)([a-zA-Z0-9\-\.]+)',
            r'(?:facebook\.com/)([a-zA-Z0-9\-\.]+)',
            r'(?:instagram\.com/)([a-zA-Z0-9\-\.]+)',
            r'(?:behance\.net/)([a-zA-Z0-9\-\.]+)',
            r'(?:dribbble\.com/)([a-zA-Z0-9\-\.]+)',
        ]

        # Job title patterns
        self.job_title_patterns = [
            r'^([A-Z][a-zA-Z\s&\-\./]+(?:Engineer|Developer|Manager|Director|Analyst|Consultant|Specialist|Coordinator|Administrator|Lead|Senior|Junior|Principal))\s*$',
            r'^(Senior|Junior|Lead|Principal|Chief)\s+([A-Z][a-zA-Z\s&\-\./]+)\s*$',
            r'^([A-Z][a-zA-Z\s&\-\./]+)\s+(Engineer|Developer|Manager|Director|Analyst)\s*$',
        ]

    def parse_resume(self, text: str, filename: str = "") -> Dict[str, Any]:
        """Parse resume text and return comprehensive structured data"""
        start_time = time.time()

        # Extract all sections with enhanced methods
        contact_info = self._extract_contact_info_comprehensive(text, filename)
        education = self._extract_education_comprehensive(text)
        experience = self._extract_experience_comprehensive(text)
        skills = self._extract_skills_comprehensive(text)
        projects = self._extract_projects_comprehensive(text)
        certifications = self._extract_certifications_comprehensive(text)
        achievements = self._extract_achievements_comprehensive(text)
        languages = self._extract_languages_comprehensive(text)
        summary = self._extract_professional_summary(text)

        processing_time = time.time() - start_time

        return {
            'ContactInformation': contact_info,
            'ProfessionalSummary': summary,
            'Education': {'EducationDetails': education},
            'EmploymentHistory': {'Positions': experience},
            'Skills': {'Raw': skills},  # Match expected format
            'Projects': projects,
            'Certifications': certifications,
            'Achievements': achievements,
            'Languages': languages,
            'ProcessingTime': processing_time,
            'QualityScore': self._calculate_quality_score(contact_info, experience, education, skills),
            'ExperienceMonths': self._calculate_total_experience_months(experience)
        }

    def _extract_contact_info_comprehensive(self, text: str, filename: str = "") -> Dict[str, Any]:
        """Extract comprehensive contact information including middle names and social media"""
        contact_info = {
            'CandidateName': {'FormattedName': '', 'GivenName': '', 'MiddleName': '', 'FamilyName': ''},
            'EmailAddresses': [],
            'Telephones': [],
            'Location': {},
            'SocialMedia': []
        }

        lines = text.split('\n')

        # Extract name (first few lines, enhanced for middle names)
        name_found = False
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            if not line or len(line) < 3:
                continue

            # Skip header-like lines
            if any(header in line.upper() for header in ['RESUME', 'CV', 'CURRICULUM VITAE', 'PROFILE']):
                continue

            # Check if this looks like a name
            if self._looks_like_name(line):
                # Extract name components including middle name
                name_parts = self._parse_name_components(line)
                if name_parts['GivenName']:
                    contact_info['CandidateName'] = name_parts
                    name_found = True
                    break

        # Extract emails
        for pattern in self.email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    email = match[0]
                else:
                    email = match
                if email not in [e['Address'] for e in contact_info['EmailAddresses']]:
                    contact_info['EmailAddresses'].append({'Address': email})

        # Extract phone numbers
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Reconstruct phone number from groups
                    if len(match) >= 3:
                        phone = f"({match[0]}) {match[1]}-{match[2]}"
                    else:
                        phone = ''.join(match)
                else:
                    phone = match

                if phone not in [p['Raw'] for p in contact_info['Telephones']]:
                    contact_info['Telephones'].append({'Raw': phone})

        # Extract social media links
        for pattern in self.social_media_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                platform = self._identify_social_platform(pattern)
                contact_info['SocialMedia'].append({
                    'Platform': platform,
                    'URL': match,
                    'Username': match
                })

        # Extract location
        location = self._extract_location(text)
        contact_info['Location'] = location

        return contact_info

    def _parse_name_components(self, name_line: str) -> Dict[str, str]:
        """Parse name into components including middle name"""
        # Clean the name line
        name_clean = re.sub(r'[,\.]', '', name_line).strip()

        # Remove common certifications and titles
        cert_pattern = r'\b(MBA|MS|PhD|Dr|Mr|Mrs|Ms|Jr|Sr|III|IV|CISSP|CISM|CISA|CRISC|PMP|ISO\s*\d+|CIS|LA|PCI|QSA|PCIP|CCNA|MCP|Security\+|Network\+)\b'
        name_clean = re.sub(cert_pattern, '', name_clean, flags=re.IGNORECASE).strip()

        # Remove multiple spaces
        name_clean = re.sub(r'\s+', ' ', name_clean)

        parts = name_clean.split()

        result = {
            'FormattedName': name_clean,
            'GivenName': '',
            'MiddleName': '',
            'FamilyName': ''
        }

        if len(parts) >= 2:
            result['GivenName'] = parts[0]
            result['FamilyName'] = parts[-1]

            # Middle name(s)
            if len(parts) > 2:
                result['MiddleName'] = ' '.join(parts[1:-1])
        elif len(parts) == 1:
            result['GivenName'] = parts[0]

        return result

    def _looks_like_name(self, line: str) -> bool:
        """Check if a line looks like a person's name"""
        line = line.strip()

        # Skip if contains email or phone
        if '@' in line or re.search(r'\d{3}[-\s]\d{3}[-\s]\d{4}', line):
            return False

        # Skip if all caps (likely headers)
        if line.isupper() and len(line) > 10:
            return False

        # Skip if contains job title keywords
        job_keywords = ['engineer', 'developer', 'manager', 'director', 'analyst', 'consultant']
        if any(keyword in line.lower() for keyword in job_keywords):
            return False

        # Should have 1-4 words, starting with capital letters
        words = line.split()
        if len(words) < 1 or len(words) > 6:
            return False

        # Check if words look like names
        for word in words[:3]:  # Check first 3 words
            if len(word) < 2:
                continue
            if not word[0].isupper():
                return False

        return True

    def _extract_professional_summary(self, text: str) -> Dict[str, Any]:
        """Extract professional summary/objective section"""
        lines = text.split('\n')
        summary_keywords = [
            'PROFESSIONAL SUMMARY', 'SUMMARY', 'OBJECTIVE', 'PROFILE',
            'CAREER SUMMARY', 'EXECUTIVE SUMMARY', 'OVERVIEW', 'ABOUT'
        ]

        summary_text = ""
        in_summary = False

        for i, line in enumerate(lines):
            line_upper = line.strip().upper()

            # Check if this is a summary section header
            if any(keyword in line_upper for keyword in summary_keywords):
                in_summary = True
                continue

            # Check if we've reached another section
            if in_summary and line_upper and line_upper in [
                'WORK EXPERIENCE', 'EMPLOYMENT HISTORY', 'EXPERIENCE',
                'EDUCATION', 'SKILLS', 'TECHNICAL SKILLS', 'PROJECTS'
            ]:
                break

            # Collect summary text
            if in_summary and line.strip():
                summary_text += line.strip() + " "

        # Also look for introductory paragraphs near the top
        if not summary_text:
            for i, line in enumerate(lines[:15]):
                if (len(line.strip()) > 50 and
                    not line.strip().isupper() and
                    not '@' in line and
                    not re.search(r'\d{3}[-\s]\d{3}[-\s]\d{4}', line)):
                    # This might be a summary
                    summary_text = line.strip()
                    break

        return {
            'Text': summary_text.strip(),
            'KeyTitles': self._extract_job_titles_from_summary(summary_text),
            'YearsExperience': self._extract_years_from_summary(summary_text)
        }

    def _extract_job_titles_from_summary(self, summary_text: str) -> List[str]:
        """Extract job titles mentioned in summary"""
        titles = []

        # Common title patterns
        title_patterns = [
            r'(Senior|Junior|Lead|Principal|Chief)\s+([A-Z][a-zA-Z\s]+(?:Engineer|Developer|Manager|Director|Analyst))',
            r'([A-Z][a-zA-Z\s]+(?:Engineer|Developer|Manager|Director|Analyst))',
            r'(Software|Data|Web|Mobile|Full[- ]?Stack|Front[- ]?End|Back[- ]?End)\s+(Engineer|Developer)',
        ]

        for pattern in title_patterns:
            matches = re.findall(pattern, summary_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    title = ' '.join(match).strip()
                else:
                    title = match.strip()
                if title and title not in titles:
                    titles.append(title)

        return titles

    def _extract_years_from_summary(self, summary_text: str) -> Optional[int]:
        """Extract years of experience from summary"""
        year_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'(\d+)\+?\s*years?\s+in',
            r'over\s+(\d+)\s+years?',
            r'more\s+than\s+(\d+)\s+years?'
        ]

        for pattern in year_patterns:
            match = re.search(pattern, summary_text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None

    def _extract_experience_comprehensive(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience with comprehensive job title detection"""
        positions = []
        lines = text.split('\n')

        # Find experience section
        experience_start = -1
        experience_end = -1

        for i, line in enumerate(lines):
            line_upper = line.strip().upper()
            if any(header in line_upper for header in [
                'WORK EXPERIENCE', 'PROFESSIONAL EXPERIENCE', 'EMPLOYMENT HISTORY',
                'EXPERIENCE', 'CAREER HISTORY', 'EMPLOYMENT'
            ]):
                experience_start = i + 1
                break

        if experience_start == -1:
            return positions

        # Find end of experience section
        for i in range(experience_start, len(lines)):
            line_upper = lines[i].strip().upper()
            if any(header in line_upper for header in [
                'EDUCATION', 'SKILLS', 'TECHNICAL SKILLS', 'PROJECTS',
                'CERTIFICATIONS', 'ACHIEVEMENTS', 'AWARDS'
            ]):
                experience_end = i
                break

        if experience_end == -1:
            experience_end = len(lines)

        experience_lines = lines[experience_start:experience_end]

        # Parse positions with improved logic
        current_position = None
        i = 0

        while i < len(experience_lines):
            line = experience_lines[i].strip()

            if not line:
                i += 1
                continue

            # Check if this line is a job title (usually appears first)
            if self._looks_like_job_title(line):
                # Start new position
                if current_position:
                    positions.append(current_position)

                current_position = {
                    'JobTitle': {'Raw': line},
                    'Employer': {'Name': {'Raw': ''}},
                    'Location': {'Municipality': '', 'Regions': [], 'CountryCode': ''},
                    'StartDate': {'Date': ''},
                    'EndDate': {'Date': ''},
                    'IsCurrent': False,
                    'Description': '',
                    'JobCategory': self._categorize_job_title(line),
                    'JobLevel': self._determine_job_level(line)
                }

                # Look for company/location in next few lines
                for j in range(i + 1, min(i + 4, len(experience_lines))):
                    next_line = experience_lines[j].strip()
                    if self._looks_like_company_location(next_line):
                        company, location = self._parse_company_location(next_line)
                        current_position['Employer']['Name']['Raw'] = company
                        if location:
                            loc_parts = self._parse_location(location)
                            current_position['Location'] = loc_parts
                        break

                # Look for dates in next few lines
                for j in range(i + 1, min(i + 4, len(experience_lines))):
                    next_line = experience_lines[j].strip()
                    if self._looks_like_date_range(next_line):
                        start_date, end_date, is_current = self._parse_date_range(next_line)
                        current_position['StartDate']['Date'] = start_date
                        current_position['EndDate']['Date'] = end_date
                        current_position['IsCurrent'] = is_current
                        break

            # Collect description lines
            elif current_position and (line.startswith('•') or line.startswith('-') or
                                    line.startswith('*') or len(line) > 20):
                if current_position['Description']:
                    current_position['Description'] += ' ' + line
                else:
                    current_position['Description'] = line

            i += 1

        # Add last position
        if current_position:
            positions.append(current_position)

        return positions

    def _looks_like_job_title(self, line: str) -> bool:
        """Check if a line looks like a job title"""
        line = line.strip()

        # Skip if empty or too short
        if len(line) < 3:
            return False

        # Skip if contains dates
        if re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\b|\d{4}', line, re.IGNORECASE):
            return False

        # Skip if contains company indicators
        if re.search(r'\b(Inc\.?|LLC|Corp\.?|Corporation|Company|Group|Technologies|Solutions|Systems)\b', line, re.IGNORECASE):
            return False

        # Skip if contains location indicators
        if re.search(r'\b(Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Drive|Dr\.?|Lane|Ln\.?|Boulevard|Blvd\.?)\b', line, re.IGNORECASE):
            return False

        # Skip if starts with bullets
        if line.startswith(('•', '-', '*', '○')):
            return False

        # Skip if it's a section header
        if line.upper() in ['WORK EXPERIENCE', 'PROFESSIONAL EXPERIENCE', 'EDUCATION', 'SKILLS', 'PROJECTS']:
            return False

        # Skip if it looks like a description or summary
        if any(word in line.lower() for word in ['specialized in', 'experienced', 'worked on', 'responsible for']):
            return False

        # Check for common job title patterns
        job_title_keywords = [
            'engineer', 'developer', 'manager', 'director', 'analyst', 'consultant',
            'specialist', 'coordinator', 'administrator', 'lead', 'senior', 'junior',
            'principal', 'chief', 'architect', 'designer', 'programmer', 'scientist'
        ]

        if any(keyword in line.lower() for keyword in job_title_keywords):
            return True

        # Check if it's in title case and reasonable length
        words = line.split()
        if (len(words) <= 5 and len(words) >= 1 and
            all(word[0].isupper() or word.lower() in ['of', 'and', 'the', 'in', 'for'] for word in words if word) and
            len(line) < 50):
            return True

        return False

    def _looks_like_company_location(self, line: str) -> bool:
        """Check if a line looks like company name and location"""
        # Should contain comma separating company and location
        if ',' not in line:
            return False

        # Should not be a job description
        if line.startswith(('•', '-', '*')):
            return False

        # Should not contain dates
        if re.search(r'\d{4}', line):
            return False

        return True

    def _parse_company_location(self, line: str) -> tuple:
        """Parse company and location from a line"""
        parts = [p.strip() for p in line.split(',')]
        company = parts[0] if parts else ''
        location = ', '.join(parts[1:]) if len(parts) > 1 else ''
        return company, location

    def _looks_like_date_range(self, line: str) -> bool:
        """Check if a line looks like a date range"""
        # Should contain year
        if not re.search(r'\d{4}', line):
            return False

        # Should contain date patterns
        date_indicators = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
                          'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                          'September', 'October', 'November', 'December', 'Present', 'Current']

        return any(indicator in line for indicator in date_indicators)

    def _parse_date_range(self, line: str) -> tuple:
        """Parse start date, end date, and current status from a line"""
        is_current = 'present' in line.lower() or 'current' in line.lower()

        # Extract start date
        start_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})', line, re.IGNORECASE)
        start_date = ''
        if start_match:
            month = start_match.group(1)
            year = start_match.group(2)
            start_date = f"{year}-{self._month_to_number(month):02d}-01"

        # Extract end date
        end_date = 'Present' if is_current else ''
        if not is_current:
            # Look for second date
            dates = re.findall(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})', line, re.IGNORECASE)
            if len(dates) >= 2:
                month = dates[1][0]
                year = dates[1][1]
                end_date = f"{year}-{self._month_to_number(month):02d}-01"

        return start_date, end_date, is_current

    def _month_to_number(self, month: str) -> int:
        """Convert month name to number"""
        month_map = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }
        return month_map.get(month.lower(), 1)

    def _categorize_job_title(self, title: str) -> str:
        """Categorize job title"""
        title_lower = title.lower()

        if any(word in title_lower for word in ['engineer', 'developer', 'programmer']):
            return 'Engineering'
        elif any(word in title_lower for word in ['manager', 'director', 'lead']):
            return 'Management'
        elif any(word in title_lower for word in ['analyst', 'scientist']):
            return 'Analysis'
        elif any(word in title_lower for word in ['designer', 'architect']):
            return 'Design'
        else:
            return 'Other'

    def _determine_job_level(self, title: str) -> str:
        """Determine job level from title"""
        title_lower = title.lower()

        if any(word in title_lower for word in ['senior', 'sr', 'lead', 'principal', 'chief']):
            return 'Senior'
        elif any(word in title_lower for word in ['junior', 'jr', 'associate', 'entry']):
            return 'Junior'
        else:
            return 'Mid-Level'

    def _extract_education_comprehensive(self, text: str) -> List[Dict[str, Any]]:
        """Extract comprehensive education information"""
        education_entries = []
        lines = text.split('\n')

        # Find education section
        education_start = -1
        for i, line in enumerate(lines):
            if 'EDUCATION' in line.upper():
                education_start = i + 1
                break

        if education_start == -1:
            return education_entries

        # Find end of education section
        education_end = len(lines)
        for i in range(education_start, len(lines)):
            line_upper = lines[i].strip().upper()
            if any(header in line_upper for header in [
                'SKILLS', 'EXPERIENCE', 'PROJECTS', 'CERTIFICATIONS'
            ]):
                education_end = i
                break

        education_lines = lines[education_start:education_end]

        current_entry = None

        for line in education_lines:
            line = line.strip()
            if not line:
                continue

            # Check if this is a degree line
            if self._looks_like_degree(line):
                if current_entry:
                    education_entries.append(current_entry)

                current_entry = {
                    'SchoolName': {'Raw': ''},
                    'Degree': {'Name': {'Raw': line}, 'Type': self._classify_degree(line)},
                    'Majors': self._extract_majors(line),
                    'StartDate': {'Date': ''},
                    'EndDate': {'Date': ''},
                    'GPA': ''
                }

            # Check if this is a school line
            elif current_entry and self._looks_like_school(line):
                current_entry['SchoolName']['Raw'] = line

            # Check if this is a date line
            elif current_entry and re.search(r'\d{4}', line):
                dates = self._parse_education_dates(line)
                current_entry['StartDate']['Date'] = dates['start']
                current_entry['EndDate']['Date'] = dates['end']

            # Check for GPA
            elif current_entry and 'gpa' in line.lower():
                gpa_match = re.search(r'(\d+\.?\d*)', line)
                if gpa_match:
                    current_entry['GPA'] = gpa_match.group(1)

        if current_entry:
            education_entries.append(current_entry)

        return education_entries

    def _looks_like_degree(self, line: str) -> bool:
        """Check if line looks like a degree"""
        degree_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'associates', 'diploma',
            'certificate', 'bs', 'ba', 'ms', 'ma', 'mba', 'phd', 'md'
        ]

        # Should contain degree keywords and not contain school indicators
        has_degree = any(keyword in line.lower() for keyword in degree_keywords)
        has_school = any(keyword in line.lower() for keyword in ['university', 'college', 'institute', 'school', 'academy'])

        return has_degree and not has_school

    def _looks_like_school(self, line: str) -> bool:
        """Check if line looks like a school name"""
        school_keywords = [
            'university', 'college', 'institute', 'school', 'academy'
        ]

        # Should contain school keywords and not contain degree indicators
        has_school = any(keyword in line.lower() for keyword in school_keywords)
        degree_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'associates', 'diploma',
            'certificate', 'bs', 'ba', 'ms', 'ma', 'mba', 'phd', 'md'
        ]
        has_degree = any(keyword in line.lower() for keyword in degree_keywords)

        return has_school and not has_degree

    def _classify_degree(self, degree_line: str) -> str:
        """Classify degree type"""
        degree_lower = degree_line.lower()

        if any(word in degree_lower for word in ['master', 'ms', 'ma', 'mba']):
            return 'masters'
        elif any(word in degree_lower for word in ['bachelor', 'bs', 'ba']):
            return 'bachelors'
        elif any(word in degree_lower for word in ['phd', 'doctorate']):
            return 'doctorate'
        elif any(word in degree_lower for word in ['associate']):
            return 'associates'
        else:
            return 'other'

    def _extract_majors(self, degree_line: str) -> List[str]:
        """Extract majors from degree line"""
        # Look for "in" keyword
        in_match = re.search(r'\bin\s+([^,\n]+)', degree_line, re.IGNORECASE)
        if in_match:
            return [in_match.group(1).strip()]

        # Look for common major keywords
        major_keywords = [
            'computer science', 'software engineering', 'electrical engineering',
            'mechanical engineering', 'business', 'marketing', 'finance',
            'accounting', 'mathematics', 'physics', 'chemistry', 'biology'
        ]

        majors = []
        for keyword in major_keywords:
            if keyword in degree_line.lower():
                majors.append(keyword.title())

        return majors

    def _parse_education_dates(self, date_line: str) -> Dict[str, str]:
        """Parse education dates"""
        years = re.findall(r'\d{4}', date_line)

        if len(years) >= 2:
            return {'start': f"{years[0]}-09-01", 'end': f"{years[1]}-06-01"}
        elif len(years) == 1:
            return {'start': f"{years[0]}-09-01", 'end': f"{int(years[0])+4}-06-01"}
        else:
            return {'start': '', 'end': ''}

    def _extract_projects_comprehensive(self, text: str) -> List[Dict[str, Any]]:
        """Extract comprehensive project information"""
        projects = []
        lines = text.split('\n')

        # Find projects section
        projects_start = -1
        for i, line in enumerate(lines):
            if 'PROJECT' in line.upper():
                projects_start = i + 1
                break

        if projects_start == -1:
            return projects

        # Find end of projects section
        projects_end = len(lines)
        for i in range(projects_start, len(lines)):
            line_upper = lines[i].strip().upper()
            if any(header in line_upper for header in [
                'SKILLS', 'EXPERIENCE', 'EDUCATION', 'CERTIFICATIONS'
            ]):
                projects_end = i
                break

        project_lines = lines[projects_start:projects_end]

        current_project = None

        for line in project_lines:
            line = line.strip()
            if not line:
                continue

            # Check if this is a project title
            if self._looks_like_project_title(line):
                if current_project:
                    projects.append(current_project)

                current_project = {
                    'Name': line,
                    'Description': '',
                    'Company': '',
                    'Role': '',
                    'StartDate': '',
                    'EndDate': '',
                    'Technologies': []
                }

            # Collect project description
            elif current_project:
                if line.startswith(('•', '-', '*')):
                    if current_project['Description']:
                        current_project['Description'] += ' ' + line
                    else:
                        current_project['Description'] = line

                # Look for technologies
                if 'technolog' in line.lower() or 'tool' in line.lower():
                    techs = self._extract_technologies_from_line(line)
                    current_project['Technologies'].extend(techs)

        if current_project:
            projects.append(current_project)

        return projects

    def _looks_like_project_title(self, line: str) -> bool:
        """Check if line looks like a project title"""
        # Should not start with bullets
        if line.startswith(('•', '-', '*')):
            return False

        # Should not be too long
        if len(line) > 100:
            return False

        # Should not be a section header
        if line.upper() in ['ACHIEVEMENTS', 'LANGUAGES', 'CERTIFICATIONS', 'SKILLS', 'EDUCATION']:
            return False

        # Should not contain obvious description keywords
        if any(word in line.lower() for word in ['implemented', 'developed', 'created', 'built', 'using']):
            return False

        # Should not be a language proficiency line
        if ':' in line and any(level in line.lower() for level in ['native', 'fluent', 'conversational', 'basic']):
            return False

        # Should be reasonably short for a title
        if len(line.split()) > 8:
            return False

        return True

    def _extract_technologies_from_line(self, line: str) -> List[str]:
        """Extract technologies from a line"""
        # Common technology patterns
        tech_patterns = [
            r'\b(Python|Java|JavaScript|React|Angular|Vue|Node\.js|Express|Django|Flask|Spring|SQL|MongoDB|PostgreSQL|MySQL|Redis|Docker|Kubernetes|AWS|Azure|GCP|Git|Jenkins|CI/CD)\b'
        ]

        technologies = []
        for pattern in tech_patterns:
            matches = re.findall(pattern, line, re.IGNORECASE)
            technologies.extend(matches)

        return technologies

    def _extract_skills_comprehensive(self, text: str) -> List[Dict[str, Any]]:
        """Extract comprehensive skills information"""
        skills = []

        # Find skills section
        lines = text.split('\n')
        skills_start = -1

        for i, line in enumerate(lines):
            line_upper = line.strip().upper()
            if any(keyword in line_upper for keyword in [
                'SKILLS', 'TECHNICAL SKILLS', 'TECHNOLOGIES', 'COMPETENCIES'
            ]):
                skills_start = i + 1
                break

        if skills_start == -1:
            return skills

        # Find end of skills section
        skills_end = len(lines)
        for i in range(skills_start, len(lines)):
            line_upper = lines[i].strip().upper()
            if any(header in line_upper for header in [
                'EXPERIENCE', 'EDUCATION', 'PROJECTS', 'CERTIFICATIONS'
            ]):
                skills_end = i
                break

        skills_lines = lines[skills_start:skills_end]

        # Parse skills from each line
        for line in skills_lines:
            line = line.strip()
            if not line:
                continue

            # Parse skills separated by commas, colons, etc.
            skill_items = self._parse_skills_from_line(line)

            for skill in skill_items:
                if skill and len(skill) > 1:
                    skills.append({
                        'Name': skill,
                        'Type': self._categorize_skill_type(skill)
                    })

        return skills[:30]  # Limit to 30 skills

    def _parse_skills_from_line(self, line: str) -> List[str]:
        """Parse individual skills from a line"""
        # Remove category labels
        if ':' in line:
            line = line.split(':', 1)[1]

        # Split by common delimiters
        delimiters = [',', ';', '•', '|', '·']
        skills = [line]

        for delimiter in delimiters:
            new_skills = []
            for skill in skills:
                new_skills.extend([s.strip() for s in skill.split(delimiter)])
            skills = new_skills

        # Clean up skills
        cleaned_skills = []
        for skill in skills:
            skill = skill.strip()
            # Remove common prefixes/suffixes
            skill = re.sub(r'^[-•*\s]+|[-•*\s]+$', '', skill)
            if skill and len(skill) > 1:
                cleaned_skills.append(skill)

        return cleaned_skills

    def _categorize_skill_type(self, skill: str) -> str:
        """Categorize skill type"""
        skill_lower = skill.lower()

        programming_languages = ['python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin']
        frameworks = ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'laravel']
        databases = ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle']
        cloud = ['aws', 'azure', 'gcp', 'docker', 'kubernetes']

        if any(lang in skill_lower for lang in programming_languages):
            return 'Programming Language'
        elif any(fw in skill_lower for fw in frameworks):
            return 'Framework'
        elif any(db in skill_lower for db in databases):
            return 'Database'
        elif any(cloud_tech in skill_lower for cloud_tech in cloud):
            return 'Cloud Technology'
        else:
            return 'Technical Skill'

    def _extract_certifications_comprehensive(self, text: str) -> List[Dict[str, Any]]:
        """Extract comprehensive certification information"""
        certifications = []
        lines = text.split('\n')

        # Find certifications section
        cert_start = -1
        for i, line in enumerate(lines):
            if 'CERTIFICATION' in line.upper():
                cert_start = i + 1
                break

        if cert_start == -1:
            # Look for certifications in text
            cert_patterns = [
                r'\b(AWS Certified|Google Cloud|Microsoft Certified|Oracle Certified|Cisco Certified|CompTIA|PMP|CISSP|CISM|CISA)\b[^.\n]*',
                r'\b([A-Z]{2,6})\s+(Certified|Certificate)\b[^.\n]*'
            ]

            for pattern in cert_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        cert_name = ' '.join(match)
                    else:
                        cert_name = match

                    certifications.append({
                        'Name': cert_name,
                        'Issuer': self._extract_cert_issuer(cert_name),
                        'IssuedYear': self._extract_cert_year(text, cert_name)
                    })

            return certifications

        # Parse certifications from dedicated section
        cert_end = len(lines)
        for i in range(cert_start, len(lines)):
            line_upper = lines[i].strip().upper()
            if any(header in line_upper for header in [
                'SKILLS', 'EXPERIENCE', 'EDUCATION', 'PROJECTS'
            ]):
                cert_end = i
                break

        cert_lines = lines[cert_start:cert_end]

        for line in cert_lines:
            line = line.strip()
            if not line:
                continue

            # Parse certification
            cert_data = self._parse_certification_line(line)
            if cert_data:
                certifications.append(cert_data)

        return certifications

    def _parse_certification_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single certification line"""
        # Look for year
        year_match = re.search(r'\b(19|20)\d{2}\b', line)
        year = year_match.group(0) if year_match else ''

        # Remove year from name
        name = re.sub(r'\b(19|20)\d{2}\b', '', line).strip()
        name = re.sub(r'\s*[-–—]\s*$', '', name).strip()

        if name:
            return {
                'Name': name,
                'Issuer': self._extract_cert_issuer(name),
                'IssuedYear': year
            }

        return None

    def _extract_cert_issuer(self, cert_name: str) -> str:
        """Extract certification issuer"""
        issuers = {
            'aws': 'Amazon Web Services',
            'google': 'Google',
            'microsoft': 'Microsoft',
            'oracle': 'Oracle',
            'cisco': 'Cisco',
            'comptia': 'CompTIA',
            'pmp': 'Project Management Institute',
            'cissp': 'ISC2',
            'cism': 'ISACA',
            'cisa': 'ISACA'
        }

        cert_lower = cert_name.lower()
        for key, issuer in issuers.items():
            if key in cert_lower:
                return issuer

        return 'Unknown'

    def _extract_cert_year(self, text: str, cert_name: str) -> str:
        """Extract certification year from text"""
        # Look for year near certification name
        cert_context = text[max(0, text.find(cert_name) - 50):text.find(cert_name) + len(cert_name) + 50]
        year_match = re.search(r'\b(19|20)\d{2}\b', cert_context)
        return year_match.group(0) if year_match else ''

    def _extract_achievements_comprehensive(self, text: str) -> List[Dict[str, Any]]:
        """Extract comprehensive achievements information"""
        achievements = []

        # Find achievements section
        lines = text.split('\n')
        achievements_start = -1

        for i, line in enumerate(lines):
            line_upper = line.strip().upper()
            if any(keyword in line_upper for keyword in [
                'ACHIEVEMENT', 'AWARD', 'HONOR', 'RECOGNITION', 'ACCOMPLISHMENT'
            ]):
                achievements_start = i + 1
                break

        if achievements_start != -1:
            # Parse achievements from dedicated section
            achievements_end = len(lines)
            for i in range(achievements_start, len(lines)):
                line_upper = lines[i].strip().upper()
                if any(header in line_upper for header in [
                    'SKILLS', 'EXPERIENCE', 'EDUCATION', 'PROJECTS'
                ]):
                    achievements_end = i
                    break

            achievement_lines = lines[achievements_start:achievements_end]

            for line in achievement_lines:
                line = line.strip()
                if line and not line.startswith(('•', '-', '*')):
                    achievements.append({
                        'Title': line,
                        'Description': '',
                        'Year': self._extract_achievement_year(line)
                    })

        # Also look for achievements mentioned throughout the text
        achievement_patterns = [
            r'(Employee of the Year|Employee of the Month)',
            r'(Published|Presented|Authored)[^.\n]*',
            r'(Award|Recognition|Honor)[^.\n]*',
            r'(Led|Managed) team of \d+',
            r'(Increased|Improved|Reduced)[^.\n]*by \d+%'
        ]

        for pattern in achievement_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    achievement_text = ' '.join(match)
                else:
                    achievement_text = match

                achievements.append({
                    'Title': achievement_text,
                    'Description': '',
                    'Year': self._extract_achievement_year(achievement_text)
                })

        return achievements[:10]  # Limit to 10 achievements

    def _extract_achievement_year(self, text: str) -> str:
        """Extract year from achievement text"""
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        return year_match.group(0) if year_match else ''

    def _extract_languages_comprehensive(self, text: str) -> List[Dict[str, Any]]:
        """Extract comprehensive language information"""
        languages = []

        # Find languages section
        lines = text.split('\n')
        languages_start = -1

        for i, line in enumerate(lines):
            line_upper = line.strip().upper()
            if 'LANGUAGE' in line_upper:
                languages_start = i + 1
                break

        if languages_start == -1:
            # Look for common language patterns
            language_patterns = [
                r'\b(English|Spanish|French|German|Chinese|Japanese|Korean|Arabic|Portuguese|Italian|Russian|Hindi)\b:\s*(Native|Fluent|Proficient|Conversational|Basic)',
                r'\b(English|Spanish|French|German|Chinese|Japanese|Korean|Arabic|Portuguese|Italian|Russian|Hindi)\b\s*[-–]\s*(Native|Fluent|Proficient|Conversational|Basic)'
            ]

            for pattern in language_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    languages.append({
                        'Language': match[0],
                        'Proficiency': match[1]
                    })

            return languages

        # Parse languages from dedicated section
        languages_end = len(lines)
        for i in range(languages_start, len(lines)):
            line_upper = lines[i].strip().upper()
            if any(header in line_upper for header in [
                'SKILLS', 'EXPERIENCE', 'EDUCATION', 'PROJECTS'
            ]):
                languages_end = i
                break

        language_lines = lines[languages_start:languages_end]

        for line in language_lines:
            line = line.strip()
            if not line:
                continue

            # Parse language and proficiency
            lang_data = self._parse_language_line(line)
            if lang_data:
                languages.append(lang_data)

        return languages

    def _parse_language_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single language line"""
        # Common patterns
        patterns = [
            r'([A-Z][a-z]+):\s*([A-Z][a-z]+)',
            r'([A-Z][a-z]+)\s*[-–]\s*([A-Z][a-z]+)',
            r'([A-Z][a-z]+)\s*\(([^)]+)\)'
        ]

        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return {
                    'Language': match.group(1),
                    'Proficiency': match.group(2)
                }

        # If no proficiency specified, assume it's a language
        if re.match(r'^[A-Z][a-z]+$', line.strip()):
            return {
                'Language': line.strip(),
                'Proficiency': 'Unknown'
            }

        return None

    def _identify_social_platform(self, pattern: str) -> str:
        """Identify social media platform from pattern"""
        if 'linkedin' in pattern:
            return 'LinkedIn'
        elif 'github' in pattern:
            return 'GitHub'
        elif 'twitter' in pattern:
            return 'Twitter'
        elif 'facebook' in pattern:
            return 'Facebook'
        elif 'instagram' in pattern:
            return 'Instagram'
        elif 'behance' in pattern:
            return 'Behance'
        elif 'dribbble' in pattern:
            return 'Dribbble'
        else:
            return 'Unknown'

    def _extract_location(self, text: str) -> Dict[str, Any]:
        """Extract location information"""
        # Look for common location patterns
        location_patterns = [
            r'([A-Z][a-z]+),\s*([A-Z]{2})\s*\d{5}',  # City, STATE ZIP
            r'([A-Z][a-z]+),\s*([A-Z]{2})',          # City, STATE
            r'([A-Z][a-z]+),\s*([A-Z][a-z\s]+)',     # City, Country
        ]

        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return {
                    'Municipality': match.group(1),
                    'Regions': [match.group(2)],
                    'CountryCode': 'US' if len(match.group(2)) == 2 else 'Unknown'
                }

        return {'Municipality': '', 'Regions': [], 'CountryCode': ''}

    def _parse_location(self, location_str: str) -> Dict[str, Any]:
        """Parse location string"""
        parts = [p.strip() for p in location_str.split(',')]

        if len(parts) >= 2:
            return {
                'Municipality': parts[0],
                'Regions': [parts[1]] if len(parts[1]) <= 3 else [parts[1][:20]],
                'CountryCode': 'US' if len(parts[1]) == 2 else 'Unknown'
            }
        else:
            return {
                'Municipality': location_str,
                'Regions': [],
                'CountryCode': 'Unknown'
            }

    def _calculate_quality_score(self, contact_info: Dict, experience: List, education: List, skills: List) -> float:
        """Calculate quality score based on extracted data"""
        score = 0

        # Contact information (25 points)
        if contact_info.get('CandidateName', {}).get('FormattedName'):
            score += 10
        if contact_info.get('EmailAddresses'):
            score += 5
        if contact_info.get('Telephones'):
            score += 5
        if contact_info.get('Location', {}).get('Municipality'):
            score += 5

        # Experience (35 points)
        if experience:
            score += 20
            if any(pos.get('JobTitle', {}).get('Raw') for pos in experience):
                score += 10
            if any(pos.get('Description') for pos in experience):
                score += 5

        # Education (20 points)
        if education:
            score += 10
            if any(edu.get('SchoolName', {}).get('Raw') for edu in education):
                score += 5
            if any(edu.get('Majors') for edu in education):
                score += 5

        # Skills (20 points)
        if skills:
            score += 20

        return min(score, 100)

    def _calculate_total_experience_months(self, experience: List) -> int:
        """Calculate total experience in months"""
        total_months = 0

        for position in experience:
            start_date = position.get('StartDate', {}).get('Date', '')
            end_date = position.get('EndDate', {}).get('Date', '')

            if start_date:
                try:
                    start_year = int(start_date.split('-')[0])
                    if end_date and end_date != 'Present':
                        end_year = int(end_date.split('-')[0])
                    else:
                        end_year = datetime.now().year

                    months = (end_year - start_year) * 12
                    total_months += months
                except:
                    pass

        return total_months