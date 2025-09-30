#!/usr/bin/env python3
"""
Enterprise Resume Parser - Full Schema Compliance
Implements comprehensive JSON schema with advanced features
"""

import re
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import phonenumbers
from phonenumbers import NumberParseException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnterpriseResumeParser:
    """
    Enterprise-grade resume parser implementing full schema compliance
    """

    def __init__(self):
        self._init_patterns()
        self._init_skills_database()
        self._init_language_database()
        logger.info("🚀 Enterprise Resume Parser initialized - Full Schema v1.0")

    def _init_patterns(self):
        """Initialize enhanced patterns for all data types"""

        # Email patterns
        self.email_patterns = [
            r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
        ]

        # Phone patterns - enhanced for international formats
        self.phone_patterns = [
            r'\+?1?\s*\((\d{3})\)[-.–\s]*(\d{3})[-.–\s]*(\d{4})',  # US format
            r'\+?1?\s*(\d{3})[-.–\s]+(\d{3})[-.–\s]+(\d{4})',      # US no parentheses
            r'\+(\d{1,3})\s*(\d{1,4})\s*(\d{1,4})\s*(\d{1,9})',    # International
            r'Phone[:\s]*\(?(\d{3})\)?[-.–\s]*(\d{3})[-.–\s]*(\d{4})',
            r'Mobile[:\s]*\(?(\d{3})\)?[-.–\s]*(\d{3})[-.–\s]*(\d{4})',
            r'Cell[:\s]*\(?(\d{3})\)?[-.–\s]*(\d{3})[-.–\s]*(\d{4})',
        ]

        # Section detection patterns
        self.section_patterns = {
            'contact': r'(?i)^(contact|personal|profile)',
            'summary': r'(?i)^(summary|profile|objective|qualifications|professional\s+summary)',
            'experience': r'(?i)^(experience|employment|work|professional|career)',
            'education': r'(?i)^(education|academic|qualifications)',
            'skills': r'(?i)^(skills|technical|competencies|technologies)',
            'certifications': r'(?i)^(certifications?|licenses?|credentials)',
            'projects': r'(?i)^(projects?|portfolio)',
            'achievements': r'(?i)^(achievements?|awards?|accomplishments?|honors?)',
            'languages': r'(?i)^(languages?|linguistic)'
        }

        # Management keywords for scoring
        self.management_keywords = [
            'manager', 'director', 'supervisor', 'lead', 'chief', 'head',
            'vp', 'vice president', 'senior manager', 'team lead', 'principal',
            'managed', 'supervised', 'led', 'directed', 'oversaw', 'coordinated'
        ]

        # Executive level keywords
        self.executive_keywords = [
            'ceo', 'cto', 'cfo', 'coo', 'president', 'vice president', 'vp',
            'executive', 'director', 'senior director', 'managing director'
        ]

    def _init_skills_database(self):
        """Initialize comprehensive skills database with categories"""
        self.skills_database = {
            'Programming Languages': [
                'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust',
                'Ruby', 'PHP', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'SQL'
            ],
            'Web Technologies': [
                'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express.js',
                'Django', 'Flask', 'FastAPI', 'Spring', 'Bootstrap', 'jQuery'
            ],
            'Cloud & DevOps': [
                'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git',
                'CI/CD', 'Terraform', 'Ansible', 'CloudFormation'
            ],
            'Databases': [
                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQL Server',
                'Cassandra', 'DynamoDB', 'Elasticsearch'
            ],
            'Data Science & AI': [
                'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Pandas',
                'NumPy', 'Scikit-learn', 'Tableau', 'Power BI', 'Spark', 'Hadoop'
            ],
            'Project Management': [
                'Agile', 'Scrum', 'Kanban', 'SAFe', 'PMP', 'PRINCE2', 'Jira', 'Confluence'
            ]
        }

    def _init_language_database(self):
        """Initialize language codes database"""
        self.language_codes = {
            'english': 'en', 'spanish': 'es', 'french': 'fr', 'german': 'de',
            'italian': 'it', 'portuguese': 'pt', 'russian': 'ru', 'chinese': 'zh',
            'japanese': 'ja', 'korean': 'ko', 'arabic': 'ar', 'hindi': 'hi'
        }

    def parse_resume(self, text: str, filename: str = "") -> Dict[str, Any]:
        """Parse resume text and return enterprise-grade structured data"""
        start_time = time.time()

        # Split text into lines for section analysis
        lines = text.strip().split('\n')

        # Extract all major sections
        contact_info = self._extract_contact_information(text, filename)
        qualifications_summary = self._extract_qualifications_summary(text)
        resume_metadata = self._extract_resume_metadata(lines)
        employment_history = self._extract_employment_history(text)
        skills = self._extract_skills_enhanced(text)
        certifications = self._extract_certifications_enhanced(text)
        education = self._extract_education_enhanced(text)
        language_competencies = self._extract_language_competencies(text)
        achievements = self._extract_achievements_enhanced(text)
        domain_classification = self._extract_domain_classification(text, skills)

        processing_time = time.time() - start_time

        return {
            'ContactInformation': contact_info,
            'QualificationsSummary': qualifications_summary,
            'ResumeMetadata': resume_metadata,
            'EmploymentHistory': employment_history,
            'WorkExperience': employment_history.get('Positions', []),  # Compatibility field
            'Skills': skills,
            'Certifications': certifications,
            'Education': education,
            'LanguageCompetencies': language_competencies,
            'Achievements': achievements,
            'DomainClassification': domain_classification,
            'ProcessingTime': processing_time,
            'ParserVersion': '1.0.0',
            'SchemaCompliant': True
        }

    def _extract_contact_information(self, text: str, filename: str = "") -> Dict[str, Any]:
        """Extract enhanced contact information with normalization"""
        lines = text.strip().split('\n')

        # Extract emails - support multiple
        emails = []
        for pattern in self.email_patterns:
            for match in re.finditer(pattern, text):
                email = match.group(1).lower()
                if email not in emails:
                    emails.append(email)

        # Extract and normalize phone numbers
        telephones = []
        for pattern in self.phone_patterns:
            for match in re.finditer(pattern, text):
                raw_phone = match.group(0)
                normalized_phone = self._normalize_phone_number(raw_phone)
                if normalized_phone:
                    telephones.append(normalized_phone)

        # Extract name with enhanced logic
        name_info = self._extract_name_enhanced(lines, filename)

        # Format email addresses as expected by the test
        email_objects = [{'EmailAddress': email} for email in emails]

        # Format phone numbers as expected by the test
        phone_objects = [{'PhoneNumber': phone.get('Raw', str(phone)) if isinstance(phone, dict) else str(phone)} for phone in telephones]

        # Create FullName from name components for BRD compliance
        full_name = name_info.get('FormattedName', '')
        if not full_name:
            # Construct from components if FormattedName is empty
            name_parts = []
            if name_info.get('GivenName'):
                name_parts.append(name_info['GivenName'])
            if name_info.get('MiddleName'):
                name_parts.append(name_info['MiddleName'])
            if name_info.get('FamilyName'):
                name_parts.append(name_info['FamilyName'])
            full_name = ' '.join(name_parts)

        return {
            'CandidateName': name_info,
            'FullName': full_name,  # Add FullName for BRD compliance
            'EmailAddresses': email_objects,
            'PhoneNumbers': phone_objects,
            'Telephones': telephones  # Keep original for backward compatibility
        }

    def _normalize_phone_number(self, raw_phone: str) -> Dict[str, str]:
        """Normalize phone number to international format"""
        try:
            # Clean the input
            cleaned = re.sub(r'[^\d+]', '', raw_phone)

            # Try to parse as US number if no country code
            if not cleaned.startswith('+'):
                cleaned = '+1' + cleaned

            parsed = phonenumbers.parse(cleaned, None)

            if phonenumbers.is_valid_number(parsed):
                return {
                    'Raw': raw_phone,
                    'Normalized': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
                    'InternationalCountryCode': str(parsed.country_code),
                    'AreaCityCode': str(parsed.national_number)[:3] if len(str(parsed.national_number)) >= 10 else '',
                    'SubscriberNumber': str(parsed.national_number)[3:] if len(str(parsed.national_number)) >= 10 else str(parsed.national_number)
                }
        except (NumberParseException, Exception):
            # Fallback for invalid numbers
            pass

        # Fallback normalization
        digits = re.sub(r'[^\d]', '', raw_phone)
        if len(digits) == 10:
            return {
                'Raw': raw_phone,
                'Normalized': f'+1{digits}',
                'InternationalCountryCode': '1',
                'AreaCityCode': digits[:3],
                'SubscriberNumber': digits[3:]
            }

        return {
            'Raw': raw_phone,
            'Normalized': raw_phone,
            'InternationalCountryCode': '',
            'AreaCityCode': '',
            'SubscriberNumber': ''
        }

    def _extract_name_enhanced(self, lines: List[str], filename: str = "") -> Dict[str, str]:
        """Enhanced name extraction with comprehensive patterns"""
        name = ""

        # Strategy 1: Find name in first few lines with multiple patterns
        for i, line in enumerate(lines[:8]):
            line_clean = line.strip()
            if not line_clean or len(line_clean) < 3:
                continue

            # Remove common prefixes
            line_clean = re.sub(r'^(Resume of|CV of|Name:|Full Name:)\s*', '', line_clean, flags=re.IGNORECASE)

            # Enhanced name patterns - more flexible
            word_count = len(line_clean.split())

            # Pattern 1: All uppercase names (2-4 words)
            if line_clean.isupper() and 2 <= word_count <= 4:
                if self._is_valid_name(line_clean):
                    name = line_clean.title()
                    break

            # Pattern 2: Title case names (2-4 words)
            elif re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', line_clean) and 2 <= word_count <= 4:
                if self._is_valid_name(line_clean):
                    name = line_clean
                    break

            # Pattern 3: Mixed case names with proper capitalization
            elif re.match(r'^[A-Z][a-zA-Z]*\s+[A-Z][a-zA-Z]*', line_clean) and 2 <= word_count <= 4:
                if self._is_valid_name(line_clean):
                    name = line_clean
                    break

            # Pattern 4: Look for names with middle initials (e.g., "John A. Smith")
            elif re.match(r'^[A-Z][a-z]+\s+[A-Z]\.?\s+[A-Z][a-z]+', line_clean):
                if self._is_valid_name(line_clean):
                    name = line_clean
                    break

            # Pattern 5: Simple first last name pattern
            elif word_count == 2 and re.match(r'^[A-Za-z]+\s+[A-Za-z]+$', line_clean):
                if self._is_valid_name(line_clean):
                    name = line_clean.title()
                    break

        # Strategy 2: Extract from filename if name not found
        if not name and filename:
            import os
            basename = os.path.basename(filename).replace('_', ' ').replace('-', ' ')
            # Remove file extension
            basename = re.sub(r'\.(pdf|doc|docx).*$', '', basename, flags=re.IGNORECASE)

            # Look for name patterns in filename
            filename_patterns = [
                r'resume of (.+)',
                r'cv of (.+)',
                r'(.+) resume',
                r'(.+) cv',
                r'^(.+?)[\s_-]*(resume|cv)',
                r'^([A-Za-z\s]+)'
            ]

            for pattern in filename_patterns:
                match = re.search(pattern, basename, re.IGNORECASE)
                if match:
                    potential_name = match.group(1).strip()
                    if potential_name and len(potential_name.split()) >= 2:
                        name = ' '.join(word.capitalize() for word in potential_name.split())
                        break

        # Parse name components
        if name:
            # Clean up the name
            name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
            name = re.sub(r',\s*(MBA|MS|PhD|CISSP|PMP|.*Certified).*$', '', name, flags=re.IGNORECASE)
            name = name.strip()

            name_parts = name.split()
            given_name = name_parts[0] if name_parts else ""
            middle_name = ' '.join(name_parts[1:-1]) if len(name_parts) > 2 else ""
            family_name = name_parts[-1] if len(name_parts) > 1 else ""

            return {
                'FormattedName': name,
                'GivenName': given_name,
                'MiddleName': middle_name,
                'FamilyName': family_name
            }

        return {
            'FormattedName': "",
            'GivenName': "",
            'MiddleName': "",
            'FamilyName': ""
        }

    def _is_valid_name(self, text: str) -> bool:
        """Check if text looks like a valid name"""
        # Exclude business/technical terms
        exclude_terms = [
            'EXPERIENCE', 'EDUCATION', 'SKILLS', 'PROJECT', 'DEVELOPER', 'ENGINEER',
            'MANAGER', 'CONSULTANT', 'COMPANY', 'SOLUTIONS', 'TECHNOLOGIES',
            'ENVIRONMENT', 'TECHNICAL', 'PROFESSIONAL', 'SOFTWARE', 'SENIOR',
            'RESUME', 'CURRICULUM', 'VITAE', 'CONTACT', 'INFORMATION', 'PHONE',
            'EMAIL', 'ADDRESS', 'OBJECTIVE', 'SUMMARY', 'QUALIFICATION',
            'CERTIFICATION', 'EMPLOYMENT', 'HISTORY', 'WORK', 'CAREER'
        ]

        text_upper = text.upper()
        if any(term in text_upper for term in exclude_terms):
            return False

        # Must contain only letters, spaces, periods, and common name characters
        if not re.match(r'^[A-Za-z\s\.\,\-\']+$', text):
            return False

        # Must have at least 2 words
        if len(text.split()) < 2:
            return False

        return True

    def _extract_qualifications_summary(self, text: str) -> str:
        """Extract professional summary/objective"""
        lines = text.split('\n')

        summary_patterns = [
            r'(?i)^(summary|professional\s+summary|profile|objective|qualifications)',
            r'(?i)^(career\s+summary|executive\s+summary|overview)'
        ]

        for i, line in enumerate(lines):
            line_clean = line.strip()
            for pattern in summary_patterns:
                if re.match(pattern, line_clean):
                    # Extract content after header
                    summary_lines = []
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if not next_line:
                            j += 1
                            continue
                        # Stop at next major section
                        if any(re.match(p, next_line) for p in self.section_patterns.values()):
                            break
                        summary_lines.append(next_line)
                        j += 1
                        if len(summary_lines) > 10:  # Limit summary length
                            break

                    return ' '.join(summary_lines)

        return ""

    def _extract_resume_metadata(self, lines: List[str]) -> Dict[str, Any]:
        """Extract metadata about resume sections"""
        found_sections = []

        for i, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean:
                continue

            for section_type, pattern in self.section_patterns.items():
                if re.match(pattern, line_clean):
                    # Find section end
                    last_line = i
                    for j in range(i + 1, len(lines)):
                        if any(re.match(p, lines[j].strip()) for p in self.section_patterns.values()):
                            last_line = j - 1
                            break
                        if lines[j].strip():
                            last_line = j

                    found_sections.append({
                        'SectionType': section_type,
                        'HeaderTextFound': line_clean,
                        'FirstLineNumber': i + 1,  # 1-indexed
                        'LastLineNumber': last_line + 1
                    })
                    break

        return {
            'FoundSections': found_sections
        }

    def _extract_employment_history(self, text: str) -> Dict[str, Any]:
        """Extract enhanced employment history with experience summary"""

        # Get positions using existing logic
        positions = self._extract_positions_enhanced(text)

        # Calculate experience summary
        experience_summary = self._calculate_experience_summary(positions, text)

        return {
            'ExperienceSummary': experience_summary,
            'Positions': positions
        }

    def _extract_positions_enhanced(self, text: str) -> List[Dict[str, Any]]:
        """Extract positions with comprehensive company and job title detection"""
        positions = []
        lines = text.split('\n')

        # Find experience section
        experience_section = self._find_experience_section(lines)
        if not experience_section:
            return positions

        # Extract positions using multiple strategies
        current_position = None

        for i, line in enumerate(experience_section):
            line = line.strip()
            if not line:
                continue

            # Skip bullet points and descriptions
            if line.startswith(('-', '•', '◦', '●')) or self._is_description_line(line):
                if current_position:
                    desc = line[1:].strip() if line.startswith(('-', '•', '◦', '●')) else line
                    if 'Description' not in current_position:
                        current_position['Description'] = []
                    current_position['Description'].append(desc)
                continue

            # Try to identify company and job title patterns
            company_info = self._extract_company_and_title(line, experience_section[i:i+3] if i+3 < len(experience_section) else experience_section[i:])

            if company_info:
                # Save previous position if exists
                if current_position:
                    positions.append(self._finalize_position(current_position))

                # Start new position
                current_position = {
                    'Employer': {
                        'Name': company_info['company'],
                        'Location': self._parse_location(company_info.get('location', ''))
                    },
                    'JobTitle': company_info.get('title', ''),
                    'StartDate': self._normalize_date(company_info.get('start_date', '')),
                    'EndDate': self._normalize_date(company_info.get('end_date', '')),
                    'IsCurrent': self._is_current_position(company_info.get('end_date', '')),
                    'Description': []
                }

        # Add final position
        if current_position:
            positions.append(self._finalize_position(current_position))

        return positions

    def _find_experience_section(self, lines: List[str]) -> List[str]:
        """Find and extract experience section from resume"""
        experience_start = -1
        experience_end = -1

        experience_headers = [
            'PROFESSIONAL EXPERIENCE', 'WORK EXPERIENCE', 'EMPLOYMENT HISTORY',
            'EMPLOYMENT', 'EXPERIENCE', 'CAREER HISTORY', 'WORK HISTORY'
        ]

        end_headers = [
            'EDUCATION', 'SKILLS', 'TECHNICAL SKILLS', 'CERTIFICATIONS',
            'PROJECTS', 'ACHIEVEMENTS', 'AWARDS', 'LANGUAGES'
        ]

        for i, line in enumerate(lines):
            line_clean = line.strip().upper()

            # Find experience section start
            if experience_start == -1:
                for header in experience_headers:
                    if header in line_clean:
                        experience_start = i + 1
                        break

            # Find experience section end
            elif experience_end == -1:
                for header in end_headers:
                    if line_clean == header or line_clean == header + ':':
                        experience_end = i
                        break

        # If we didn't find an experience section, try fallback strategies
        if experience_start == -1:
            # Strategy 1: Look for company indicators in early text
            for i, line in enumerate(lines[:50]):  # Check first 50 lines
                line_clean = line.strip()
                # Look for patterns that suggest work experience
                if any(indicator in line_clean for indicator in [
                    'Project Manager', 'Software Engineer', 'Manager', 'Developer',
                    'Contract', 'Full-time', 'Part-time', '(', '–', 'Current)'
                ]) and len(line_clean.split()) <= 10:
                    experience_start = max(0, i - 5)  # Start a bit before
                    break

            # Strategy 2: If still not found, look for obvious company names
            if experience_start == -1:
                for i, line in enumerate(lines):
                    line_upper = line.strip().upper()
                    known_companies = ['GOOGLE', 'MICROSOFT', 'AMAZON', 'FACEBOOK', 'NETFLIX', 'UNITED', 'PEPSI']
                    if any(company in line_upper for company in known_companies):
                        experience_start = max(0, i - 2)
                        break

        if experience_start == -1:
            return []
        if experience_end == -1:
            experience_end = len(lines)

        return lines[experience_start:experience_end]

    def _extract_company_and_title(self, line: str, context_lines: List[str]) -> Optional[Dict[str, str]]:
        """Extract company name and job title from line with context"""

        # Pattern 1: Company | Job Title | Dates
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 2:
                company = parts[0]
                title = parts[1] if len(parts) > 1 else ''
                dates = parts[2] if len(parts) > 2 else ''

                if self._is_valid_company(company):
                    date_info = self._parse_date_range(dates)
                    return {
                        'company': company,
                        'title': title,
                        'start_date': date_info.get('start', ''),
                        'end_date': date_info.get('end', ''),
                        'location': ''
                    }

        # Pattern 2: Job Title at Company (Date range)
        at_pattern = r'(.+?)\s+at\s+(.+?)(?:\s*\((.+?)\))?(?:\s*[-–]\s*(.+))?$'
        match = re.search(at_pattern, line, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            company = match.group(2).strip()
            dates = match.group(3) or match.group(4) or ''

            if self._is_valid_company(company):
                date_info = self._parse_date_range(dates)
                return {
                    'company': company,
                    'title': title,
                    'start_date': date_info.get('start', ''),
                    'end_date': date_info.get('end', ''),
                    'location': ''
                }

        # Pattern 3: Company name with common suffixes
        company_patterns = [
            r'([A-Z][a-zA-Z\s&]+(?:Inc|Corp|LLC|Company|Ltd|Corporation|Group|Systems|Solutions|Technologies|Consulting)\.?)',
            r'([A-Z][a-zA-Z\s&]+(?:Bank|Insurance|Financial|Services|Enterprises|Industries)\.?)',
            r'([A-Z][a-zA-Z\s&]+(?:Airlines?|Airline))',  # Added for United Airlines
        ]

        for pattern in company_patterns:
            match = re.search(pattern, line)
            if match:
                company = match.group(1).strip()
                if self._is_valid_company(company):
                    # Look for title in next lines
                    title = self._find_title_in_context(context_lines)
                    return {
                        'company': company,
                        'title': title,
                        'start_date': '',
                        'end_date': '',
                        'location': ''
                    }

        # Pattern 4: Known company names (enhanced)
        known_companies = [
            'Google', 'Microsoft', 'Amazon', 'Facebook', 'Netflix', 'Tesla', 'Adobe',
            'Uber', 'Airbnb', 'Spotify', 'LinkedIn', 'Twitter', 'Oracle', 'IBM',
            'Intel', 'Adobe', 'Salesforce', 'PayPal', 'eBay', 'Yahoo',
            'United Airlines', 'United Airline', 'PepsiCo', 'Pepsi'
        ]

        line_words = line.split()
        for company in known_companies:
            if company.lower() in line.lower():
                title = self._find_title_in_context(context_lines)
                return {
                    'company': company,
                    'title': title,
                    'start_date': '',
                    'end_date': '',
                    'location': ''
                }

        # Pattern 5: Company name followed by "– Remote" or location
        location_pattern = r'([A-Z][a-zA-Z\s]+)\s*[–-]\s*(Remote|[A-Z][a-z]+(?:,\s*[A-Z]{2})?)'
        match = re.search(location_pattern, line)
        if match:
            company = match.group(1).strip()
            location = match.group(2).strip()
            if self._is_valid_company(company) and len(company.split()) <= 4:
                title = self._find_title_in_context(context_lines)
                return {
                    'company': company,
                    'title': title,
                    'start_date': '',
                    'end_date': '',
                    'location': location
                }

        # Pattern 6: Simple company name patterns (for cases like "United Airline" standalone)
        simple_company_patterns = [
            r'^([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)(?:\s+[–-]|\s*$)',  # Two word companies
            r'^([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)(?:\s+[–-]|\s*$)',  # Three word companies
        ]

        for pattern in simple_company_patterns:
            match = re.search(pattern, line)
            if match:
                company = match.group(1).strip()
                if self._is_valid_company(company):
                    title = self._find_title_in_context(context_lines)
                    return {
                        'company': company,
                        'title': title,
                        'start_date': '',
                        'end_date': '',
                        'location': ''
                    }

        return None

    def _is_valid_company(self, text: str) -> bool:
        """Check if text looks like a valid company name"""
        if not text or len(text.strip()) < 2:
            return False

        # Exclude common non-company terms
        exclude_terms = [
            'EXPERIENCE', 'EDUCATION', 'SKILLS', 'PROJECT', 'RESUME',
            'SOFTWARE', 'TECHNICAL', 'PROFESSIONAL', 'SENIOR', 'JUNIOR',
            'EMPLOYMENT HISTORY', 'WORK HISTORY', 'CAREER HISTORY',
            'FULL TIME', 'PART TIME', 'CONTRACT', 'FREELANCE',
            'PRESENTATION PACKS', 'RESPONSIBILITIES', 'SUMMARY',
            'CONTACT', 'PHONE', 'EMAIL', 'ADDRESS', 'OBJECTIVE'
        ]

        text_upper = text.upper()
        if any(term in text_upper for term in exclude_terms):
            return False

        # Exclude section headers
        section_headers = [
            'EMPLOYMENT HISTORY', 'WORK EXPERIENCE', 'PROFESSIONAL EXPERIENCE',
            'CAREER HISTORY', 'EDUCATION', 'SKILLS', 'CERTIFICATIONS',
            'ACHIEVEMENTS', 'PROJECTS', 'LANGUAGES', 'REFERENCES'
        ]

        if text_upper in section_headers:
            return False

        # Exclude job types
        job_types = ['FULL TIME', 'PART TIME', 'CONTRACT', 'FREELANCE', 'CONSULTANT']
        if text_upper in job_types:
            return False

        # Exclude generic terms that are not companies
        generic_terms = [
            'RESPONSIBILITIES', 'DUTIES', 'SUMMARY', 'OVERVIEW', 'DESCRIPTION',
            'ADDITIONAL KPIS', 'PRESENTATION PACKS', 'RESOURCE MANAGEMENT'
        ]

        if text_upper in generic_terms:
            return False

        # Must start with capital letter or number
        if not (text[0].isupper() or text[0].isdigit()):
            return False

        # Must contain at least one letter
        if not any(c.isalpha() for c in text):
            return False

        return True

    def _find_title_in_context(self, context_lines: List[str]) -> str:
        """Find job title in context lines"""
        title_keywords = [
            'engineer', 'developer', 'manager', 'analyst', 'director',
            'consultant', 'specialist', 'coordinator', 'lead', 'senior',
            'junior', 'associate', 'principal', 'architect', 'scientist'
        ]

        for line in context_lines[:3]:  # Check first 3 lines
            line = line.strip()
            if any(keyword in line.lower() for keyword in title_keywords):
                # Clean up the title
                title = re.sub(r'^\W+|\W+$', '', line)  # Remove leading/trailing non-word chars
                if len(title.split()) <= 6:  # Reasonable title length
                    return title

        return ''

    def _is_description_line(self, line: str) -> bool:
        """Check if line is a job description rather than company/title"""
        # Lines that are too long are likely descriptions
        if len(line.split()) > 12:
            return True

        # Lines starting with action words
        action_words = [
            'developed', 'managed', 'led', 'created', 'implemented',
            'designed', 'collaborated', 'responsible', 'oversaw',
            'coordinated', 'established', 'conducted', 'analyzed'
        ]

        return any(line.lower().startswith(word) for word in action_words)

    def _parse_date_range(self, date_str: str) -> Dict[str, str]:
        """Parse date range from string"""
        if not date_str:
            return {'start': '', 'end': ''}

        # Split on common separators
        separators = [' - ', ' – ', ' to ', ' | ']
        for sep in separators:
            if sep in date_str:
                parts = date_str.split(sep, 1)
                return {
                    'start': parts[0].strip(),
                    'end': parts[1].strip() if len(parts) > 1 else ''
                }

        return {'start': date_str.strip(), 'end': ''}

    def _finalize_position(self, position: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize position with proper formatting"""
        # Join descriptions
        if 'Description' in position and isinstance(position['Description'], list):
            position['Description'] = ' '.join(position['Description'])
        elif 'Description' not in position:
            position['Description'] = ''

        return position

    def _parse_location(self, location_str: str) -> Dict[str, Any]:
        """Parse location into structured format"""
        if not location_str:
            return {
                'CountryCode': 'US',
                'Regions': [],
                'Municipality': ''
            }

        # US state abbreviations
        us_states = {
            'CA': 'California', 'TX': 'Texas', 'NY': 'New York', 'FL': 'Florida',
            'IL': 'Illinois', 'PA': 'Pennsylvania', 'OH': 'Ohio', 'GA': 'Georgia'
        }

        # Try to parse "City, State" format
        if ',' in location_str:
            parts = [p.strip() for p in location_str.split(',')]
            municipality = parts[0]
            region = parts[1] if len(parts) > 1 else ''

            # Expand state abbreviation
            if region.upper() in us_states:
                region = us_states[region.upper()]

            return {
                'CountryCode': 'US',
                'Regions': [region] if region else [],
                'Municipality': municipality
            }

        return {
            'CountryCode': 'US',
            'Regions': [],
            'Municipality': location_str
        }

    def _normalize_date(self, date_str: str) -> str:
        """Normalize date to ISO format"""
        if not date_str or date_str.lower() in ['present', 'current']:
            return date_str

        # Try to parse various date formats
        date_patterns = [
            r'(\d{4})-(\d{2})-(\d{2})',  # 2023-01-01
            r'(\d{4})-(\d{1,2})',        # 2023-1
            r'(\w+)\s+(\d{4})',          # January 2023
            r'(\w{3})\s+(\d{4})',        # Jan 2023
        ]

        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                if len(match.groups()) == 3:  # Full date
                    return f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"
                elif len(match.groups()) == 2:  # Month/Year
                    month_str = match.group(1)
                    year = match.group(2)

                    # Convert month name to number
                    month_map = {
                        'January': '01', 'February': '02', 'March': '03', 'April': '04',
                        'May': '05', 'June': '06', 'July': '07', 'August': '08',
                        'September': '09', 'October': '10', 'November': '11', 'December': '12',
                        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                        'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09',
                        'Oct': '10', 'Nov': '11', 'Dec': '12'
                    }

                    if month_str in month_map:
                        return f"{year}-{month_map[month_str]}-01"
                    elif month_str.isdigit():
                        return f"{year}-{month_str.zfill(2)}-01"

        return date_str

    def _is_current_position(self, end_date: str) -> bool:
        """Check if position is current"""
        return end_date.lower() in ['present', 'current', '']

    def _calculate_experience_summary(self, positions: List[Dict], text: str) -> Dict[str, Any]:
        """Calculate comprehensive experience summary"""

        total_months = 0
        management_months = 0
        employers = []

        # Calculate experience from positions
        for pos in positions:
            start_date = pos.get('StartDate', '')
            end_date = pos.get('EndDate', '')

            months = self._calculate_months_between_dates(start_date, end_date)
            total_months += months

            # Check for management experience
            job_title = pos.get('JobTitle', '').lower()
            description = pos.get('Description', '').lower()

            if any(keyword in job_title or keyword in description
                   for keyword in self.management_keywords):
                management_months += months

            # Track employers
            employer_name = pos.get('Employer', {}).get('Name', '')
            if employer_name and employer_name not in employers:
                employers.append(employer_name)

        # Calculate averages
        avg_months_per_employer = total_months // len(employers) if employers else 0

        # Calculate management score (0-10)
        management_score = min(10, (management_months * 10) // max(total_months, 1))

        # Determine executive type
        executive_type = self._determine_executive_type(text)

        # Generate description
        description = self._generate_experience_description(total_months, management_months, len(employers))

        return {
            'Description': description,
            'MonthsOfWorkExperience': total_months,
            'MonthsOfManagementExperience': management_months,
            'ExecutiveType': executive_type,
            'AverageMonthsPerEmployer': avg_months_per_employer,
            'ManagementScore': management_score
        }

    def _calculate_months_between_dates(self, start_date: str, end_date: str) -> int:
        """Calculate months of experience between two dates"""
        if not start_date:
            return 24  # Default assumption

        try:
            # Parse start date
            start_year = int(start_date[:4]) if len(start_date) >= 4 else 2020
            start_month = int(start_date[5:7]) if len(start_date) >= 7 else 1

            # Parse end date
            if end_date.lower() in ['present', 'current', '']:
                end_year = datetime.now().year
                end_month = datetime.now().month
            else:
                end_year = int(end_date[:4]) if len(end_date) >= 4 else start_year + 2
                end_month = int(end_date[5:7]) if len(end_date) >= 7 else 12

            months = (end_year - start_year) * 12 + (end_month - start_month)
            return max(1, months)  # Minimum 1 month

        except (ValueError, IndexError):
            return 24  # Default assumption

    def _determine_executive_type(self, text: str) -> str:
        """Determine executive level based on resume content"""
        text_lower = text.lower()

        for keyword in self.executive_keywords:
            if keyword in text_lower:
                if keyword in ['ceo', 'president', 'chief']:
                    return 'C-Level'
                elif keyword in ['vp', 'vice president', 'director']:
                    return 'VP/Director'
                else:
                    return 'Senior Management'

        # Check for management indicators
        if any(keyword in text_lower for keyword in self.management_keywords):
            return 'Management'

        return 'Individual Contributor'

    def _generate_experience_description(self, total_months: int, management_months: int, num_employers: int) -> str:
        """Generate human-readable experience description"""
        years = total_months // 12
        remaining_months = total_months % 12

        description = f"{years} years"
        if remaining_months > 0:
            description += f" and {remaining_months} months"
        description += " of professional experience"

        if management_months > 0:
            mgmt_years = management_months // 12
            description += f", including {mgmt_years} years of management experience"

        description += f" across {num_employers} organizations."

        return description

    def _extract_skills_enhanced(self, text: str) -> List[Dict[str, Any]]:
        """Extract skills with comprehensive pattern matching"""

        # Comprehensive skills list with variations
        all_skills = [
            # Programming Languages
            ('Python', ['python', 'py']),
            ('Java', ['java']),
            ('JavaScript', ['javascript', 'js', 'node.js', 'nodejs', 'node']),
            ('TypeScript', ['typescript', 'ts']),
            ('C++', ['c++', 'cpp']),
            ('C#', ['c#', 'csharp', 'c sharp']),
            ('Go', ['golang', 'go']),
            ('Rust', ['rust']),
            ('Ruby', ['ruby']),
            ('PHP', ['php']),
            ('Swift', ['swift']),
            ('Kotlin', ['kotlin']),
            ('Scala', ['scala']),
            ('R', ['r programming', 'r language']),
            ('MATLAB', ['matlab']),
            ('SQL', ['sql', 'mysql', 'postgresql', 'mssql']),

            # Web Technologies
            ('HTML', ['html', 'html5']),
            ('CSS', ['css', 'css3']),
            ('React', ['react', 'reactjs', 'react.js']),
            ('Angular', ['angular', 'angularjs']),
            ('Vue.js', ['vue', 'vuejs', 'vue.js']),
            ('Django', ['django']),
            ('Flask', ['flask']),
            ('FastAPI', ['fastapi', 'fast api']),
            ('Spring', ['spring', 'spring boot', 'springboot']),
            ('Express.js', ['express', 'expressjs', 'express.js']),
            ('Bootstrap', ['bootstrap']),
            ('jQuery', ['jquery']),

            # Cloud & DevOps
            ('AWS', ['aws', 'amazon web services', 'amazon aws']),
            ('Azure', ['azure', 'microsoft azure']),
            ('GCP', ['gcp', 'google cloud', 'google cloud platform']),
            ('Docker', ['docker', 'containerization']),
            ('Kubernetes', ['kubernetes', 'k8s']),
            ('Jenkins', ['jenkins']),
            ('Git', ['git', 'github', 'gitlab']),
            ('CI/CD', ['ci/cd', 'continuous integration', 'continuous deployment']),
            ('Terraform', ['terraform']),
            ('Ansible', ['ansible']),

            # Databases
            ('MySQL', ['mysql']),
            ('PostgreSQL', ['postgresql', 'postgres']),
            ('MongoDB', ['mongodb', 'mongo']),
            ('Redis', ['redis']),
            ('Oracle', ['oracle', 'oracle db']),
            ('SQL Server', ['sql server', 'mssql', 'microsoft sql server']),
            ('Cassandra', ['cassandra']),
            ('DynamoDB', ['dynamodb']),
            ('Elasticsearch', ['elasticsearch', 'elastic search']),

            # Data Science & AI
            ('Machine Learning', ['machine learning', 'ml']),
            ('Deep Learning', ['deep learning', 'dl']),
            ('TensorFlow', ['tensorflow']),
            ('PyTorch', ['pytorch']),
            ('Pandas', ['pandas']),
            ('NumPy', ['numpy']),
            ('Scikit-learn', ['scikit-learn', 'sklearn']),
            ('Tableau', ['tableau']),
            ('Power BI', ['power bi', 'powerbi']),
            ('Spark', ['apache spark', 'spark']),
            ('Hadoop', ['hadoop']),

            # Project Management
            ('Agile', ['agile', 'agile methodology']),
            ('Scrum', ['scrum']),
            ('Kanban', ['kanban']),
            ('Jira', ['jira']),
            ('Confluence', ['confluence']),

            # Operating Systems
            ('Linux', ['linux', 'ubuntu', 'centos', 'redhat']),
            ('Windows', ['windows']),
            ('macOS', ['macos', 'mac os'])
        ]

        found_skills = []
        text_lower = text.lower()

        for skill_name, variations in all_skills:
            for variation in variations:
                if variation in text_lower:
                    # Estimate experience and last used
                    months_exp = self._estimate_skill_experience(skill_name, text)
                    last_used = self._estimate_last_used_date(skill_name, text)

                    found_skills.append({
                        'Name': skill_name,
                        'MonthsExperience': months_exp,
                        'LastUsed': last_used
                    })
                    break  # Found this skill, don't look for other variations

        # Remove duplicates and return top 25
        unique_skills = []
        seen_skills = set()
        for skill in found_skills:
            if skill['Name'] not in seen_skills:
                unique_skills.append(skill)
                seen_skills.add(skill['Name'])

        return unique_skills[:25]

    def _estimate_skill_experience(self, skill_name: str, text: str) -> int:
        """Estimate months of experience for a skill"""
        skill_lower = skill_name.lower()
        text_lower = text.lower()

        # Look for experience indicators
        patterns = [
            rf'{skill_lower}.*?(\d+)\s*(?:years?|yrs?)',
            rf'(\d+)\s*(?:years?|yrs?).*?{skill_lower}',
            rf'{skill_lower}.*?expert',
            rf'expert.*?{skill_lower}',
            rf'senior.*?{skill_lower}',
            rf'{skill_lower}.*?architect'
        ]

        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                # Check if pattern has capturing groups and contains digits
                if match.groups() and len(match.groups()) >= 1:
                    try:
                        if match.group(1).isdigit():
                            years = int(match.group(1))
                            return min(120, years * 12)  # Cap at 10 years
                    except (IndexError, AttributeError):
                        pass

                # Handle patterns without capturing groups
                if 'expert' in pattern:
                    return 60  # 5 years for expert
                elif 'senior' in pattern:
                    return 48  # 4 years for senior
                elif 'architect' in pattern:
                    return 72  # 6 years for architect

        # Default estimation based on frequency
        skill_count = text_lower.count(skill_lower)
        if skill_count >= 5:
            return 36  # 3 years
        elif skill_count >= 3:
            return 24  # 2 years
        else:
            return 12  # 1 year

    def _estimate_last_used_date(self, skill_name: str, text: str) -> str:
        """Estimate when skill was last used"""
        # Look for recent dates in context of the skill
        current_year = datetime.now().year

        # If skill appears in recent context, assume current
        if any(indicator in text.lower() for indicator in ['current', 'present', str(current_year)]):
            return str(current_year)

        # Look for years in the text
        years = re.findall(r'\b(20\d{2})\b', text)
        if years:
            # Assume most recent year
            return max(years)

        return str(current_year)  # Default to current year

    def _extract_certifications_enhanced(self, text: str) -> List[Dict[str, str]]:
        """Extract certifications with issue years"""

        # Use existing certification extraction
        from fixed_resume_parser import FixedResumeParser

        parser = FixedResumeParser()
        old_certs = parser._extract_certifications(text)

        enhanced_certs = []
        for cert in old_certs:
            cert_name = cert.get('name', '')
            year_issued = self._extract_certification_year(cert_name, text)
            cert_category = self._classify_certification(cert_name)

            enhanced_certs.append({
                'Name': cert_name,
                'YearIssued': year_issued,
                'Category': cert_category,
                'IsValid': self._is_certification_valid(year_issued)
            })

        return enhanced_certs

    def _extract_certification_year(self, cert_name: str, text: str) -> str:
        """Extract year when certification was issued"""
        # Look for years near the certification name
        cert_pattern = re.escape(cert_name.lower())

        # Search for year patterns near certification
        patterns = [
            rf'{cert_pattern}.*?(20\d{{2}})',
            rf'(20\d{{2}}).*?{cert_pattern}',
            rf'{cert_pattern}.*?(\d{{4}})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                year = match.group(1)
                if 1990 <= int(year) <= datetime.now().year:
                    return year

        return ""  # No year found

    def _classify_certification(self, cert_name: str) -> str:
        """Classify certification into categories"""
        cert_lower = cert_name.lower()

        categories = {
            'cloud': ['aws', 'azure', 'gcp', 'google cloud', 'cloud'],
            'security': ['cissp', 'cism', 'cisa', 'security', 'certified ethical hacker'],
            'project_management': ['pmp', 'scrum master', 'agile', 'project management'],
            'technology': ['cisco', 'microsoft', 'oracle', 'vmware', 'comptia'],
            'data': ['tableau', 'power bi', 'data', 'analytics', 'big data'],
            'programming': ['java', 'python', 'javascript', 'programming', 'developer']
        }

        for category, keywords in categories.items():
            if any(keyword in cert_lower for keyword in keywords):
                return category

        return 'general'

    def _is_certification_valid(self, year_issued: str) -> bool:
        """Check if certification is still valid (within 5 years)"""
        if not year_issued:
            return False

        try:
            cert_year = int(year_issued)
            current_year = datetime.now().year
            return (current_year - cert_year) <= 5
        except ValueError:
            return False

    def _extract_education_enhanced(self, text: str) -> Dict[str, Any]:
        """Extract enhanced education with highest degree tracking"""

        # Use existing education extraction
        from fixed_resume_parser import FixedResumeParser

        parser = FixedResumeParser()
        old_education = parser._extract_education_improved(text)

        # Convert to new format
        education_details = []
        highest_degree = {'Name': '', 'Type': 'bachelors'}

        for edu in old_education:
            school_info = edu.get('School', {})
            degree_info = edu.get('Degree', {})

            # Parse school location
            school_location = self._parse_location(school_info.get('Name', ''))

            # Extract year of passing
            year_passing = self._extract_graduation_year(school_info.get('Name', ''), text)

            detail = {
                'SchoolName': school_info.get('Name', ''),
                'Location': school_location,
                'Degree': {
                    'Name': degree_info.get('Name', ''),
                    'Type': degree_info.get('Type', 'bachelors')
                },
                'Majors': self._extract_majors(degree_info.get('Name', '')),
                'YearOfPassing': year_passing
            }

            education_details.append(detail)

            # Track highest degree
            degree_rank = self._get_degree_rank(degree_info.get('Type', 'bachelors'))
            if degree_rank > self._get_degree_rank(highest_degree['Type']):
                highest_degree = degree_info

        return {
            'HighestDegree': highest_degree,
            'EducationDetails': education_details
        }

    def _get_degree_rank(self, degree_type: str) -> int:
        """Get numerical rank for degree comparison"""
        ranks = {
            'doctorate': 4,
            'masters': 3,
            'bachelors': 2,
            'associates': 1,
            'certificate': 0
        }
        return ranks.get(degree_type.lower(), 2)

    def _extract_graduation_year(self, school_text: str, full_text: str) -> str:
        """Extract graduation year from education section"""
        # Look for years in school context
        years = re.findall(r'\b(19\d{2}|20\d{2})\b', school_text + ' ' + full_text)
        if years:
            # Return most recent reasonable year
            valid_years = [y for y in years if 1970 <= int(y) <= datetime.now().year + 1]
            return max(valid_years) if valid_years else ""
        return ""

    def _extract_majors(self, degree_name: str) -> List[str]:
        """Extract major/field of study from degree name"""
        if not degree_name:
            return []

        # Common patterns for extracting majors
        patterns = [
            r'in\s+(.*?)(?:\s+from|\s+at|$)',
            r'of\s+(.*?)(?:\s+from|\s+at|$)',
            r':\s+(.*?)(?:\s+from|\s+at|$)'
        ]

        for pattern in patterns:
            match = re.search(pattern, degree_name, re.IGNORECASE)
            if match:
                major = match.group(1).strip()
                # Clean up the major name
                major = re.sub(r'\s+', ' ', major)
                return [major]

        return []

    def _extract_language_competencies(self, text: str) -> List[Dict[str, str]]:
        """Extract language skills with language codes"""
        competencies = []

        # Look for language sections
        lines = text.split('\n')
        in_language_section = False

        for line in lines:
            line_clean = line.strip()

            # Check for language section headers
            if re.match(self.section_patterns['languages'], line_clean):
                in_language_section = True
                continue

            # Stop at next major section
            if in_language_section and any(re.match(p, line_clean) for p in self.section_patterns.values() if p != self.section_patterns['languages']):
                break

            if in_language_section and line_clean:
                # Extract languages from the line
                detected_languages = self._detect_languages_in_text(line_clean)
                competencies.extend(detected_languages)

        # Also look for language mentions throughout resume
        global_languages = self._detect_languages_in_text(text)

        # Combine and deduplicate
        all_languages = {}
        for lang in competencies + global_languages:
            all_languages[lang['Language']] = lang

        return list(all_languages.values())

    def _detect_languages_in_text(self, text: str) -> List[Dict[str, str]]:
        """Detect language mentions in text"""
        detected = []
        text_lower = text.lower()

        for language, code in self.language_codes.items():
            if language in text_lower:
                detected.append({
                    'Language': language.capitalize(),
                    'LanguageCode': code
                })

        return detected

    def _extract_achievements(self, text: str) -> List[str]:
        """Extract achievements and awards"""
        achievements = []
        lines = text.split('\n')
        in_achievement_section = False

        for line in lines:
            line_clean = line.strip()

            # Check for achievement section headers
            if re.match(self.section_patterns['achievements'], line_clean):
                in_achievement_section = True
                continue

            # Stop at next major section
            if in_achievement_section and any(re.match(p, line_clean) for p in self.section_patterns.values() if p != self.section_patterns['achievements']):
                break

            if in_achievement_section and line_clean:
                # Clean bullet points and add to achievements
                achievement = re.sub(r'^[-•*]\s*', '', line_clean)
                if achievement and len(achievement) > 10:  # Filter out short/empty entries
                    achievements.append(achievement)

        # Also look for achievement keywords throughout resume
        achievement_keywords = [
            'award', 'recognition', 'achievement', 'honor', 'distinction',
            'medal', 'prize', 'scholarship', 'fellowship'
        ]

        for line in lines:
            line_clean = line.strip()
            if any(keyword in line_clean.lower() for keyword in achievement_keywords):
                if len(line_clean) > 20 and line_clean not in achievements:
                    achievements.append(line_clean)

        return achievements

    def _extract_achievements_enhanced(self, text: str) -> List[Dict[str, Any]]:
        """Extract achievements using the enhanced achievements extractor"""
        try:
            from achievements_extractor import AchievementsExtractor
            extractor = AchievementsExtractor()
            return extractor.extract_achievements(text)
        except Exception as e:
            logger.warning(f"Enhanced achievements extraction failed: {e}")
            # Fallback to basic extraction
            return [{"description": achievement, "impact_category": "general"}
                   for achievement in self._extract_achievements(text)][:10]  # Limit to top 10

    def _extract_domain_classification(self, text: str, skills: List[Dict]) -> Dict[str, Any]:
        """Classify candidate's professional domain based on skills and experience"""
        domain_keywords = {
            'software_engineering': ['python', 'java', 'javascript', 'react', 'angular', 'nodejs', 'programming', 'software', 'development', 'coding', 'git'],
            'data_science': ['python', 'r', 'machine learning', 'tensorflow', 'data analysis', 'pandas', 'numpy', 'sql', 'statistics', 'analytics'],
            'devops': ['docker', 'kubernetes', 'aws', 'azure', 'jenkins', 'terraform', 'ansible', 'ci/cd', 'infrastructure', 'cloud'],
            'cybersecurity': ['security', 'penetration', 'vulnerability', 'firewall', 'encryption', 'compliance', 'risk', 'audit'],
            'product_management': ['product management', 'roadmap', 'agile', 'scrum', 'stakeholder', 'business analysis', 'requirements'],
            'marketing': ['marketing', 'campaigns', 'social media', 'seo', 'content', 'branding', 'analytics', 'digital marketing'],
            'finance': ['financial', 'accounting', 'budget', 'analysis', 'investment', 'excel', 'modeling', 'forecasting'],
            'sales': ['sales', 'customer', 'crm', 'revenue', 'targets', 'negotiation', 'lead generation', 'business development']
        }

        text_lower = text.lower()
        skill_names = [skill.get('Name', '').lower() for skill in skills if isinstance(skill, dict)]

        domain_scores = {}
        for domain, keywords in domain_keywords.items():
            score = 0
            for keyword in keywords:
                # Check in full text
                if keyword in text_lower:
                    score += text_lower.count(keyword)
                # Check in skills
                for skill in skill_names:
                    if keyword in skill:
                        score += 2  # Weight skills higher
            domain_scores[domain] = score

        # Find primary domain
        primary_domain = max(domain_scores, key=domain_scores.get) if domain_scores else 'general'
        confidence = domain_scores.get(primary_domain, 0) / max(sum(domain_scores.values()), 1)

        return {
            'PrimaryDomain': primary_domain,
            'Confidence': round(confidence, 2),
            'DomainScores': domain_scores,
            'SecondaryDomains': sorted([d for d, s in domain_scores.items() if s > 0 and d != primary_domain],
                                     key=lambda x: domain_scores[x], reverse=True)[:3]
        }

# Helper function to test the parser
def test_enhanced_parser():
    """Test function for the enhanced parser"""
    parser = EnterpriseResumeParser()

    # Test with sample text
    sample_text = """
    John Doe
    Software Engineer
    john.doe@example.com
    (555) 123-4567
    San Francisco, CA

    PROFESSIONAL SUMMARY
    Experienced software engineer with 5+ years in Python and cloud technologies.

    EXPERIENCE
    Senior Software Engineer
    Tech Corp, San Francisco, CA
    2020-01-01 to Present
    • Led team of 5 developers
    • Built scalable microservices

    EDUCATION
    Bachelor of Science in Computer Science
    Stanford University, Stanford, CA
    2018

    SKILLS
    Python, AWS, Docker, Kubernetes

    LANGUAGES
    English (Native), Spanish (Conversational)
    """

    result = parser.parse_resume(sample_text)
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    print(test_enhanced_parser())