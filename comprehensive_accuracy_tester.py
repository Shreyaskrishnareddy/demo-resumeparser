#!/usr/bin/env python3
"""
Comprehensive Resume Parser Accuracy Tester
Tests each resume and compares output with actual content for 100% accuracy
"""

import os
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any
import docx
import fitz  # PyMuPDF
import re

class ComprehensiveAccuracyTester:
    def __init__(self, server_url="http://localhost:8001"):
        self.server_url = server_url
        self.results = {}
        self.total_accuracy = 0.0

    def extract_text_from_file(self, file_path: str) -> str:
        """Extract raw text from file for manual verification"""
        try:
            if file_path.endswith('.pdf'):
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text
            elif file_path.endswith(('.doc', '.docx')):
                try:
                    doc = docx.Document(file_path)
                    text = ""
                    for paragraph in doc.paragraphs:
                        text += paragraph.text + "\n"
                    return text
                except:
                    return f"Could not extract text from {file_path}"
            elif file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return ""
        except Exception as e:
            return f"Error extracting text: {str(e)}"

    def extract_expected_data_from_text(self, text: str, filename: str) -> Dict:
        """Extract expected data from raw resume text for comparison"""
        expected_data = {
            'name': self._extract_expected_name(text, filename),
            'email': self._extract_expected_email(text),
            'phone': self._extract_expected_phone(text),
            'education': self._extract_expected_education(text),
            'experience': self._extract_expected_experience(text),
            'skills': self._extract_expected_skills(text),
            'achievements': self._extract_expected_achievements(text),
            'languages': self._extract_expected_languages(text)
        }
        return expected_data

    def _extract_expected_name(self, text: str, filename: str) -> str:
        """Extract expected name from text and filename"""
        lines = text.strip().split('\n')

        # Try filename first
        if 'Connal_Jackson' in filename or 'Connal Jackson' in filename:
            return "Connal Jackson"
        elif 'Ashok_Kumar' in filename or 'Ashok Kumar' in filename:
            return "Ashok Kumar"
        elif 'PRANAY_REDDY' in filename:
            return "Pranay Reddy"

        # Try first few lines
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 3 and len(line) < 50:
                # Check if line looks like a name
                if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', line) or line.isupper():
                    # Skip common headers
                    if not any(word in line.upper() for word in ['RESUME', 'CV', 'CURRICULUM', 'PROFILE', 'ENGINEER', 'DEVELOPER', 'MANAGER']):
                        return line

        return "Unknown"

    def _extract_expected_email(self, text: str) -> str:
        """Extract expected email from text"""
        email_pattern = r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else ""

    def _extract_expected_phone(self, text: str) -> str:
        """Extract expected phone from text"""
        phone_patterns = [
            r'\((\d{3})\)[-.–\s]*(\d{3})[-.–\s]*(\d{4})',
            r'(\d{3})[-.–\s]+(\d{3})[-.–\s]+(\d{4})',
            r'\+1?\s*(\d{3})[-.–)\s]*(\d{3})[-.–)\s]*(\d{4})',
        ]

        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) >= 3:
                    return f"({match.group(1)}) {match.group(2)}-{match.group(3)}"
                else:
                    return match.group(0)
        return ""

    def _extract_expected_education(self, text: str) -> List[Dict]:
        """Extract expected education from text"""
        education = []
        lines = text.split('\n')

        # Look in EDUCATION section only
        in_education_section = False
        for i, line in enumerate(lines):
            line_clean = line.strip()

            # Detect education section
            if line_clean.upper() == 'EDUCATION':
                in_education_section = True
                continue

            # Detect section end
            if in_education_section and line_clean.upper() in ['TECHNICAL SKILLS', 'SKILLS', 'EXPERIENCE', 'CERTIFICATIONS']:
                break

            if in_education_section and line_clean:
                # Look for degree patterns in education section only
                degree_match = re.match(r'^(Bachelor of Science|Bachelor of Arts|Master of Science|Master of Arts|Bachelor|Master|PhD|MBA|BSc|MSc|BA|MA|BS|MS)\s*(?:of|in)?\s*(.+)', line_clean, re.IGNORECASE)
                if degree_match:
                    degree_type = degree_match.group(1)
                    field = degree_match.group(2).strip() if degree_match.group(2) else ""

                    # Only include if field looks like academic field
                    if field and len(field) > 2 and not any(exclude in field.lower() for exclude in ['gpa', 'relevant', 'coursework', '|']):
                        degree_name = f"{degree_type} {field}".strip()
                        school_name = self._find_nearby_school(text, i, lines)

                        education.append({
                            'degree': degree_name,
                            'school': school_name
                        })

        return education

    def _find_nearby_school(self, text: str, line_index: int, lines: List[str]) -> str:
        """Find school name near degree mention"""
        # Check next few lines for university/college
        for i in range(line_index + 1, min(len(lines), line_index + 4)):
            line = lines[i].strip()
            if any(keyword in line.lower() for keyword in ['university', 'college', 'institute']) and '|' in line:
                return line.split('|')[0].strip()
            elif any(keyword in line.lower() for keyword in ['university', 'college', 'institute']):
                return line

        return ""

    def _extract_expected_experience(self, text: str) -> List[Dict]:
        """Extract expected experience from text"""
        experience = []

        # Look for company patterns
        company_patterns = [
            r'([A-Z][a-zA-Z\s&]+(?:Inc|Corp|LLC|Ltd|Company|Solutions|Technologies|Systems))',
            r'([A-Z][a-zA-Z\s&]+),\s*([A-Z]{2})',  # Company, State format
        ]

        for pattern in company_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                company = match.group(1).strip()
                if len(company) > 3 and len(company) < 100:
                    experience.append({
                        'company': company,
                        'position': self._find_nearby_position(text, match.start())
                    })

        return experience

    def _find_nearby_position(self, text: str, position: int) -> str:
        """Find job position near company mention"""
        lines = text.split('\n')
        current_line_num = text[:position].count('\n')

        job_keywords = ['Engineer', 'Developer', 'Manager', 'Analyst', 'Specialist', 'Director', 'Consultant']

        for i in range(max(0, current_line_num-2), min(len(lines), current_line_num+3)):
            line = lines[i].strip()
            if any(keyword in line for keyword in job_keywords):
                return line

        return ""

    def _extract_expected_skills(self, text: str) -> List[str]:
        """Extract expected skills from text"""
        skills = []

        # Common technical skills
        common_skills = [
            'Python', 'Java', 'JavaScript', 'React', 'Angular', 'Node.js', 'SQL', 'MySQL',
            'PostgreSQL', 'MongoDB', 'AWS', 'Azure', 'Docker', 'Kubernetes', 'Git',
            'Machine Learning', 'Data Science', 'Analytics', 'Agile', 'Scrum'
        ]

        text_upper = text.upper()
        for skill in common_skills:
            if skill.upper() in text_upper:
                skills.append(skill)

        return skills

    def _extract_expected_achievements(self, text: str) -> List[str]:
        """Extract expected achievements from text"""
        achievements = []

        # Look for achievement patterns
        achievement_patterns = [
            r'(Won|Received|Awarded|Achieved|Earned)\s+([^.\n]+)',
            r'(Increased|Improved|Reduced|Saved)\s+([^.\n]+)',
            r'(\d+%)\s+(improvement|increase|reduction)',
        ]

        for pattern in achievement_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                achievement = match.group(0).strip()
                if len(achievement) > 10:
                    achievements.append(achievement)

        return achievements

    def _extract_expected_languages(self, text: str) -> List[str]:
        """Extract expected languages from text"""
        languages = []

        common_languages = [
            'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese',
            'Chinese', 'Japanese', 'Korean', 'Arabic', 'Russian', 'Hindi'
        ]

        for language in common_languages:
            if language in text:
                languages.append(language)

        return languages

    def test_resume_file(self, file_path: str) -> Dict:
        """Test individual resume file"""
        print(f"\n🔍 Testing: {os.path.basename(file_path)}")

        # Extract actual text for comparison
        actual_text = self.extract_text_from_file(file_path)
        expected_data = self.extract_expected_data_from_text(actual_text, file_path)

        # Test with API
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.server_url}/api/parse", files=files)

            if response.status_code == 200:
                parsed_data = response.json()

                # Compare results
                accuracy_results = self.compare_results(expected_data, parsed_data)

                result = {
                    'filename': os.path.basename(file_path),
                    'success': True,
                    'expected_data': expected_data,
                    'parsed_data': parsed_data,
                    'accuracy_results': accuracy_results,
                    'overall_accuracy': accuracy_results['overall_score'],
                    'processing_time': parsed_data.get('ProcessingTime', 0)
                }

                print(f"✅ Parsed successfully - Accuracy: {accuracy_results['overall_score']:.1f}%")
                return result

            else:
                print(f"❌ API Error: {response.status_code}")
                return {
                    'filename': os.path.basename(file_path),
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'overall_accuracy': 0.0
                }

        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return {
                'filename': os.path.basename(file_path),
                'success': False,
                'error': str(e),
                'overall_accuracy': 0.0
            }

    def compare_results(self, expected: Dict, parsed: Dict) -> Dict:
        """Compare expected vs parsed results"""
        scores = {}

        # Name comparison
        expected_name = expected['name'].lower().strip()
        parsed_name = parsed.get('ContactInformation', {}).get('CandidateName', {}).get('FormattedName', '').lower().strip()
        scores['name_score'] = 100.0 if expected_name in parsed_name or parsed_name in expected_name else 0.0

        # Email comparison
        expected_email = expected['email'].lower().strip()
        parsed_emails = parsed.get('ContactInformation', {}).get('EmailAddresses', [])
        # Handle both string and dict formats for email addresses
        if parsed_emails:
            if isinstance(parsed_emails[0], dict):
                parsed_email = parsed_emails[0].get('Address', parsed_emails[0].get('EmailAddress', ''))
            else:
                parsed_email = str(parsed_emails[0])
        else:
            parsed_email = ''
        scores['email_score'] = 100.0 if expected_email == parsed_email.lower().strip() else 0.0

        # Phone comparison
        expected_phone = expected['phone']
        parsed_phones = parsed.get('ContactInformation', {}).get('Telephones', [])
        # Handle both string and dict formats for phone numbers
        if parsed_phones:
            if isinstance(parsed_phones[0], dict):
                parsed_phone = parsed_phones[0].get('Raw', parsed_phones[0].get('FormattedNumber', ''))
            else:
                parsed_phone = str(parsed_phones[0])
        else:
            parsed_phone = ''
        scores['phone_score'] = 100.0 if self._normalize_phone(expected_phone) == self._normalize_phone(parsed_phone) else 0.0

        # Education comparison
        expected_education = expected['education']
        parsed_education = parsed.get('Education', {}).get('EducationDetails', [])
        scores['education_score'] = self._compare_education(expected_education, parsed_education)

        # Experience comparison
        expected_experience = expected['experience']
        parsed_experience = parsed.get('EmploymentHistory', {}).get('Positions', [])
        scores['experience_score'] = self._compare_experience(expected_experience, parsed_experience)

        # Skills comparison
        expected_skills = expected['skills']
        raw_skills = parsed.get('Skills', [])
        parsed_skills = []
        for skill in raw_skills:
            if isinstance(skill, dict):
                # Handle dict format - try multiple possible key names
                skill_name = skill.get('name', skill.get('Name', skill.get('SkillName', str(skill))))
                parsed_skills.append(str(skill_name))
            else:
                # Handle string format
                parsed_skills.append(str(skill))
        scores['skills_score'] = self._compare_lists(expected_skills, parsed_skills)

        # Calculate overall score
        weights = {
            'name_score': 0.25,
            'email_score': 0.15,
            'phone_score': 0.10,
            'education_score': 0.20,
            'experience_score': 0.20,
            'skills_score': 0.10
        }

        overall_score = sum(scores[key] * weights[key] for key in weights)
        scores['overall_score'] = overall_score

        return scores

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number for comparison"""
        return re.sub(r'[^\d]', '', phone)

    def _compare_education(self, expected: List[Dict], parsed: List[Dict]) -> float:
        """Compare education lists"""
        if not expected and not parsed:
            return 100.0
        if not expected or not parsed:
            return 0.0

        matches = 0
        for exp_edu in expected:
            for parsed_edu in parsed:
                exp_degree = exp_edu.get('degree', '').lower()

                # Handle both old complex format and new simplified format
                if isinstance(parsed_edu.get('Degree'), dict):
                    # Old complex format: {'Degree': {'Name': '...'}}
                    parsed_degree = parsed_edu.get('Degree', {}).get('Name', '').lower()
                else:
                    # New simplified format: {'degree': '...'}
                    parsed_degree = parsed_edu.get('degree', '').lower()

                if exp_degree in parsed_degree or parsed_degree in exp_degree:
                    matches += 1
                    break

        return (matches / len(expected)) * 100.0 if expected else 0.0

    def _compare_experience(self, expected: List[Dict], parsed: List[Dict]) -> float:
        """Compare experience lists"""
        if not expected and not parsed:
            return 100.0
        if not expected or not parsed:
            return 0.0

        matches = 0
        for exp_exp in expected:
            for parsed_exp in parsed:
                exp_company = exp_exp.get('company', '').lower()

                # Handle both old complex format and new simplified format
                if isinstance(parsed_exp.get('Employer'), dict):
                    # Old complex format: {'Employer': {'Name': '...'}}
                    parsed_company = parsed_exp.get('Employer', {}).get('Name', '').lower()
                else:
                    # Handle other possible formats
                    parsed_company = str(parsed_exp.get('Employer', parsed_exp.get('company', ''))).lower()

                if exp_company in parsed_company or parsed_company in exp_company:
                    matches += 1
                    break

        return (matches / len(expected)) * 100.0 if expected else 0.0

    def _compare_lists(self, expected: List[str], parsed: List[str]) -> float:
        """Compare string lists"""
        if not expected and not parsed:
            return 100.0
        if not expected:
            return 100.0  # No expectations
        if not parsed:
            return 0.0

        expected_lower = [item.lower() for item in expected]
        parsed_lower = [item.lower() for item in parsed]

        matches = sum(1 for exp in expected_lower if any(exp in parsed_item for parsed_item in parsed_lower))
        return (matches / len(expected)) * 100.0

    def run_comprehensive_test(self):
        """Run comprehensive test on all resume files"""
        print("🚀 COMPREHENSIVE RESUME PARSER ACCURACY TEST")
        print("=" * 60)

        # Find all resume files
        test_files = []

        # Add files from original test directory
        original_test_dir = "/home/great/claudeprojects/parser/test_resumes/Test Resumes/"
        if os.path.exists(original_test_dir):
            for file in os.listdir(original_test_dir):
                if file.endswith(('.pdf', '.doc', '.docx', '.txt')) and ':Zone.Identifier' not in file:
                    test_files.append(os.path.join(original_test_dir, file))

        # Add files from current project
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith(('.pdf', '.doc', '.docx', '.txt')) and 'parser_env' not in root:
                    file_path = os.path.join(root, file)
                    if any(keyword in file.lower() for keyword in ['resume', 'cv']) or 'uploads' in root:
                        test_files.append(file_path)

        print(f"📁 Found {len(test_files)} test files")

        results = []
        total_accuracy = 0.0
        successful_tests = 0

        for file_path in test_files:
            result = self.test_resume_file(file_path)
            results.append(result)

            if result['success']:
                total_accuracy += result['overall_accuracy']
                successful_tests += 1

        # Calculate final statistics
        average_accuracy = total_accuracy / successful_tests if successful_tests > 0 else 0.0

        print(f"\n📊 FINAL RESULTS")
        print("=" * 60)
        print(f"Total files tested: {len(test_files)}")
        print(f"Successful parses: {successful_tests}")
        print(f"Failed parses: {len(test_files) - successful_tests}")
        print(f"Average accuracy: {average_accuracy:.1f}%")

        # Detailed results
        print(f"\n📋 DETAILED RESULTS")
        print("-" * 60)
        for result in results:
            status = "✅" if result['success'] else "❌"
            accuracy = result['overall_accuracy'] if result['success'] else 0.0
            print(f"{status} {result['filename']:<30} Accuracy: {accuracy:.1f}%")

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"comprehensive_accuracy_test_results_{timestamp}.json"

        final_results = {
            'timestamp': timestamp,
            'total_files': len(test_files),
            'successful_tests': successful_tests,
            'failed_tests': len(test_files) - successful_tests,
            'average_accuracy': average_accuracy,
            'detailed_results': results
        }

        with open(output_file, 'w') as f:
            json.dump(final_results, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")

        if average_accuracy < 100.0:
            print(f"\n⚠️  ACCURACY ISSUES FOUND")
            print("=" * 60)
            for result in results:
                if result['success'] and result['overall_accuracy'] < 100.0:
                    print(f"\n🔍 {result['filename']} - {result['overall_accuracy']:.1f}% accuracy")
                    if 'accuracy_results' in result:
                        for key, score in result['accuracy_results'].items():
                            if key != 'overall_score' and score < 100.0:
                                print(f"   - {key}: {score:.1f}%")

        return final_results

if __name__ == "__main__":
    tester = ComprehensiveAccuracyTester()
    results = tester.run_comprehensive_test()