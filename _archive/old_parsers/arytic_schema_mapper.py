#!/usr/bin/env python3
"""
Arytic Database Schema Mapper
Maps parsed resume data to Arytic's database schema for all tables
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class AryticSchemaMapper:
    def __init__(self):
        """Initialize the Arytic schema mapper"""
        self.schema_version = "1.0"
        self.mapping_timestamp = datetime.now().isoformat()

        # Arytic table schemas
        self.table_schemas = self._define_arytic_tables()

        logger.info("🗄️ Arytic Schema Mapper initialized")

    def _define_arytic_tables(self) -> Dict[str, Dict]:
        """Define Arytic database table schemas"""
        return {
            'candidates': {
                'primary_key': 'candidate_id',
                'fields': {
                    'candidate_id': 'BIGINT AUTO_INCREMENT',
                    'first_name': 'VARCHAR(100)',
                    'middle_name': 'VARCHAR(100)',
                    'last_name': 'VARCHAR(100)',
                    'full_name': 'VARCHAR(300)',
                    'email_primary': 'VARCHAR(255)',
                    'email_secondary': 'VARCHAR(255)',
                    'phone_primary': 'VARCHAR(50)',
                    'phone_secondary': 'VARCHAR(50)',
                    'current_title': 'VARCHAR(200)',
                    'current_company': 'VARCHAR(200)',
                    'total_experience_years': 'DECIMAL(4,2)',
                    'current_salary': 'DECIMAL(12,2)',
                    'expected_salary': 'DECIMAL(12,2)',
                    'location_city': 'VARCHAR(100)',
                    'location_state': 'VARCHAR(100)',
                    'location_country': 'VARCHAR(100)',
                    'linkedin_url': 'VARCHAR(500)',
                    'portfolio_url': 'VARCHAR(500)',
                    'availability_status': 'ENUM("available", "employed", "between_jobs")',
                    'visa_status': 'VARCHAR(100)',
                    'willing_to_relocate': 'BOOLEAN',
                    'preferred_work_mode': 'ENUM("remote", "onsite", "hybrid")',
                    'resume_file_path': 'VARCHAR(1000)',
                    'resume_text': 'LONGTEXT',
                    'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                    'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP',
                    'source': 'VARCHAR(100)',
                    'recruiter_notes': 'TEXT'
                }
            },

            'candidate_skills': {
                'primary_key': 'skill_id',
                'foreign_keys': {'candidate_id': 'candidates.candidate_id'},
                'fields': {
                    'skill_id': 'BIGINT AUTO_INCREMENT',
                    'candidate_id': 'BIGINT',
                    'skill_name': 'VARCHAR(200)',
                    'skill_category': 'VARCHAR(100)',
                    'proficiency_level': 'ENUM("beginner", "intermediate", "advanced", "expert")',
                    'years_of_experience': 'DECIMAL(4,2)',
                    'months_of_experience': 'INT',
                    'last_used_date': 'DATE',
                    'is_primary_skill': 'BOOLEAN',
                    'is_currently_using': 'BOOLEAN',
                    'endorsement_count': 'INT DEFAULT 0',
                    'certification_available': 'BOOLEAN',
                    'skill_synonym_group': 'VARCHAR(100)',
                    'match_percentage': 'DECIMAL(5,2)',
                    'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                }
            },

            'candidate_experience': {
                'primary_key': 'experience_id',
                'foreign_keys': {'candidate_id': 'candidates.candidate_id'},
                'fields': {
                    'experience_id': 'BIGINT AUTO_INCREMENT',
                    'candidate_id': 'BIGINT',
                    'company_name': 'VARCHAR(200)',
                    'job_title': 'VARCHAR(200)',
                    'job_family': 'VARCHAR(100)',
                    'seniority_level': 'ENUM("junior", "mid", "senior", "lead", "principal", "executive")',
                    'start_date': 'DATE',
                    'end_date': 'DATE',
                    'is_current': 'BOOLEAN',
                    'duration_months': 'INT',
                    'job_description': 'TEXT',
                    'key_achievements': 'TEXT',
                    'technologies_used': 'TEXT',
                    'industry': 'VARCHAR(100)',
                    'company_size': 'VARCHAR(50)',
                    'management_experience': 'BOOLEAN',
                    'team_size_managed': 'INT',
                    'location_city': 'VARCHAR(100)',
                    'location_country': 'VARCHAR(100)',
                    'employment_type': 'ENUM("full_time", "part_time", "contract", "internship", "freelance")',
                    'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                }
            },

            'candidate_education': {
                'primary_key': 'education_id',
                'foreign_keys': {'candidate_id': 'candidates.candidate_id'},
                'fields': {
                    'education_id': 'BIGINT AUTO_INCREMENT',
                    'candidate_id': 'BIGINT',
                    'institution_name': 'VARCHAR(300)',
                    'degree_type': 'VARCHAR(100)',
                    'field_of_study': 'VARCHAR(200)',
                    'major': 'VARCHAR(200)',
                    'minor': 'VARCHAR(200)',
                    'start_date': 'DATE',
                    'graduation_date': 'DATE',
                    'gpa': 'DECIMAL(4,3)',
                    'honors': 'VARCHAR(200)',
                    'location_city': 'VARCHAR(100)',
                    'location_country': 'VARCHAR(100)',
                    'thesis_title': 'VARCHAR(500)',
                    'relevant_coursework': 'TEXT',
                    'academic_achievements': 'TEXT',
                    'is_highest_degree': 'BOOLEAN',
                    'verification_status': 'ENUM("verified", "pending", "not_verified")',
                    'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                }
            },

            'candidate_certifications': {
                'primary_key': 'certification_id',
                'foreign_keys': {'candidate_id': 'candidates.candidate_id'},
                'fields': {
                    'certification_id': 'BIGINT AUTO_INCREMENT',
                    'candidate_id': 'BIGINT',
                    'certification_name': 'VARCHAR(300)',
                    'issuing_organization': 'VARCHAR(200)',
                    'issue_date': 'DATE',
                    'expiry_date': 'DATE',
                    'credential_id': 'VARCHAR(100)',
                    'verification_url': 'VARCHAR(500)',
                    'skill_area': 'VARCHAR(200)',
                    'certification_level': 'VARCHAR(100)',
                    'is_active': 'BOOLEAN',
                    'renewal_required': 'BOOLEAN',
                    'industry_recognition': 'ENUM("high", "medium", "low")',
                    'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                }
            },

            'candidate_projects': {
                'primary_key': 'project_id',
                'foreign_keys': {'candidate_id': 'candidates.candidate_id'},
                'fields': {
                    'project_id': 'BIGINT AUTO_INCREMENT',
                    'candidate_id': 'BIGINT',
                    'project_name': 'VARCHAR(300)',
                    'project_description': 'TEXT',
                    'role_in_project': 'VARCHAR(200)',
                    'start_date': 'DATE',
                    'end_date': 'DATE',
                    'duration_months': 'INT',
                    'technologies_used': 'TEXT',
                    'project_url': 'VARCHAR(500)',
                    'github_url': 'VARCHAR(500)',
                    'team_size': 'INT',
                    'project_type': 'ENUM("personal", "professional", "academic", "open_source")',
                    'industry_domain': 'VARCHAR(100)',
                    'achievements': 'TEXT',
                    'challenges_faced': 'TEXT',
                    'business_impact': 'TEXT',
                    'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                }
            },

            'candidate_languages': {
                'primary_key': 'language_id',
                'foreign_keys': {'candidate_id': 'candidates.candidate_id'},
                'fields': {
                    'language_id': 'BIGINT AUTO_INCREMENT',
                    'candidate_id': 'BIGINT',
                    'language_name': 'VARCHAR(100)',
                    'language_code': 'VARCHAR(10)',
                    'proficiency_level': 'ENUM("basic", "conversational", "professional", "native")',
                    'speaking_level': 'ENUM("basic", "intermediate", "advanced", "native")',
                    'writing_level': 'ENUM("basic", "intermediate", "advanced", "native")',
                    'reading_level': 'ENUM("basic", "intermediate", "advanced", "native")',
                    'is_native': 'BOOLEAN',
                    'certification_available': 'BOOLEAN',
                    'certification_name': 'VARCHAR(200)',
                    'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                }
            },

            'candidate_achievements': {
                'primary_key': 'achievement_id',
                'foreign_keys': {'candidate_id': 'candidates.candidate_id'},
                'fields': {
                    'achievement_id': 'BIGINT AUTO_INCREMENT',
                    'candidate_id': 'BIGINT',
                    'achievement_title': 'VARCHAR(300)',
                    'achievement_description': 'TEXT',
                    'achievement_type': 'ENUM("award", "publication", "patent", "recognition", "promotion")',
                    'date_achieved': 'DATE',
                    'issuing_organization': 'VARCHAR(200)',
                    'quantified_result': 'VARCHAR(200)',
                    'impact_metrics': 'TEXT',
                    'context': 'VARCHAR(500)',
                    'verification_url': 'VARCHAR(500)',
                    'industry_relevance': 'ENUM("high", "medium", "low")',
                    'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                }
            },

            'job_applications': {
                'primary_key': 'application_id',
                'foreign_keys': {
                    'candidate_id': 'candidates.candidate_id',
                    'job_posting_id': 'job_postings.job_posting_id'
                },
                'fields': {
                    'application_id': 'BIGINT AUTO_INCREMENT',
                    'candidate_id': 'BIGINT',
                    'job_posting_id': 'BIGINT',
                    'application_date': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                    'application_status': 'ENUM("applied", "screening", "interviewed", "offered", "hired", "rejected")',
                    'resume_version_used': 'VARCHAR(100)',
                    'cover_letter': 'TEXT',
                    'recruiter_notes': 'TEXT',
                    'interview_feedback': 'TEXT',
                    'match_score': 'DECIMAL(5,2)',
                    'skills_match_percentage': 'DECIMAL(5,2)',
                    'experience_match_percentage': 'DECIMAL(5,2)',
                    'location_match': 'BOOLEAN',
                    'salary_match': 'BOOLEAN',
                    'application_source': 'VARCHAR(100)',
                    'referral_source': 'VARCHAR(200)',
                    'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'
                }
            },

            'skill_synonyms': {
                'primary_key': 'synonym_id',
                'fields': {
                    'synonym_id': 'BIGINT AUTO_INCREMENT',
                    'primary_skill': 'VARCHAR(200)',
                    'synonym_skill': 'VARCHAR(200)',
                    'match_percentage': 'DECIMAL(5,2)',
                    'skill_family': 'VARCHAR(100)',
                    'is_version_variant': 'BOOLEAN',
                    'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                }
            },

            'job_title_mappings': {
                'primary_key': 'mapping_id',
                'fields': {
                    'mapping_id': 'BIGINT AUTO_INCREMENT',
                    'job_title': 'VARCHAR(200)',
                    'job_family': 'VARCHAR(100)',
                    'seniority_level': 'INT',
                    'alternative_titles': 'TEXT',
                    'skill_requirements': 'TEXT',
                    'industry_context': 'VARCHAR(100)',
                    'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                }
            }
        }

    def map_to_arytic_schema(self, parsed_resume: Dict) -> Dict[str, Any]:
        """
        Map parsed resume data to Arytic database schema

        Args:
            parsed_resume: Output from enterprise resume parser

        Returns:
            Dictionary with data mapped to all Arytic tables
        """
        try:
            # Generate unique candidate ID for this mapping
            candidate_uuid = str(uuid.uuid4())

            mapped_data = {
                'mapping_metadata': {
                    'candidate_uuid': candidate_uuid,
                    'mapping_timestamp': self.mapping_timestamp,
                    'schema_version': self.schema_version,
                    'source_parser': 'enterprise_resume_parser'
                },
                'table_data': {}
            }

            # Map to each table
            mapped_data['table_data']['candidates'] = self._map_candidates_table(parsed_resume, candidate_uuid)
            mapped_data['table_data']['candidate_skills'] = self._map_skills_table(parsed_resume, candidate_uuid)
            mapped_data['table_data']['candidate_experience'] = self._map_experience_table(parsed_resume, candidate_uuid)
            mapped_data['table_data']['candidate_education'] = self._map_education_table(parsed_resume, candidate_uuid)
            mapped_data['table_data']['candidate_certifications'] = self._map_certifications_table(parsed_resume, candidate_uuid)
            mapped_data['table_data']['candidate_projects'] = self._map_projects_table(parsed_resume, candidate_uuid)
            mapped_data['table_data']['candidate_languages'] = self._map_languages_table(parsed_resume, candidate_uuid)
            mapped_data['table_data']['candidate_achievements'] = self._map_achievements_table(parsed_resume, candidate_uuid)

            return mapped_data

        except Exception as e:
            logger.error(f"Schema mapping failed: {e}")
            return {
                'error': str(e),
                'mapping_metadata': {
                    'failed_at': datetime.now().isoformat()
                }
            }

    def _map_candidates_table(self, resume: Dict, candidate_uuid: str) -> Dict:
        """Map to candidates table"""
        contact_info = resume.get('ContactInformation', {})
        quals_summary = resume.get('QualificationsSummary', {})
        employment = resume.get('EmploymentHistory', [])

        current_job = next((job for job in employment if job.get('IsCurrent', False)), {})

        # Extract primary email and phone
        emails = contact_info.get('EmailAddresses', [])
        phones = contact_info.get('PhoneNumbers', [])

        primary_email = emails[0].get('EmailAddress', '') if emails else ''
        secondary_email = emails[1].get('EmailAddress', '') if len(emails) > 1 else ''

        primary_phone = phones[0].get('Raw', '') if phones else ''
        secondary_phone = phones[1].get('Raw', '') if len(phones) > 1 else ''

        return {
            'candidate_uuid': candidate_uuid,
            'first_name': contact_info.get('FirstName', ''),
            'middle_name': contact_info.get('MiddleName', ''),
            'last_name': contact_info.get('LastName', ''),
            'full_name': contact_info.get('FullName', ''),
            'email_primary': primary_email,
            'email_secondary': secondary_email,
            'phone_primary': primary_phone,
            'phone_secondary': secondary_phone,
            'current_title': current_job.get('JobTitle', ''),
            'current_company': current_job.get('Employer', ''),
            'total_experience_years': quals_summary.get('YearsOfExperience', 0),
            'current_salary': None,  # Not available in parsed data
            'expected_salary': None,  # Not available in parsed data
            'location_city': contact_info.get('Location', {}).get('City', ''),
            'location_state': contact_info.get('Location', {}).get('State', ''),
            'location_country': contact_info.get('Location', {}).get('Country', ''),
            'linkedin_url': next((url['Url'] for url in contact_info.get('WebAddresses', []) if 'linkedin' in url.get('Url', '').lower()), ''),
            'portfolio_url': next((url['Url'] for url in contact_info.get('WebAddresses', []) if 'portfolio' in url.get('Type', '').lower()), ''),
            'availability_status': 'employed' if current_job else 'between_jobs',
            'visa_status': None,  # Not available in parsed data
            'willing_to_relocate': None,  # Not available in parsed data
            'preferred_work_mode': None,  # Not available in parsed data
            'resume_file_path': None,  # To be set externally
            'resume_text': None,  # To be set externally
            'source': 'resume_upload',
            'recruiter_notes': None
        }

    def _map_skills_table(self, resume: Dict, candidate_uuid: str) -> List[Dict]:
        """Map to candidate_skills table"""
        skills = resume.get('Skills', [])
        skill_records = []

        for skill in skills:
            skill_records.append({
                'candidate_uuid': candidate_uuid,
                'skill_name': skill.get('Name', ''),
                'skill_category': skill.get('Type', 'technical'),
                'proficiency_level': self._map_proficiency_level(skill.get('Level', '')),
                'years_of_experience': skill.get('YearsExperience', {}).get('Value', 0),
                'months_of_experience': skill.get('MonthsExperience', 0),
                'last_used_date': skill.get('LastUsed', ''),
                'is_primary_skill': skill.get('IsPrimary', False),
                'is_currently_using': skill.get('IsCurrentlyUsing', False),
                'endorsement_count': 0,
                'certification_available': False,
                'skill_synonym_group': skill.get('SynonymGroup', ''),
                'match_percentage': skill.get('MatchPercentage', 100)
            })

        return skill_records

    def _map_experience_table(self, resume: Dict, candidate_uuid: str) -> List[Dict]:
        """Map to candidate_experience table"""
        employment = resume.get('EmploymentHistory', [])
        experience_records = []

        for job in employment:
            experience_records.append({
                'candidate_uuid': candidate_uuid,
                'company_name': job.get('Employer', ''),
                'job_title': job.get('JobTitle', ''),
                'job_family': job.get('JobFamily', ''),
                'seniority_level': self._map_seniority_level(job.get('JobTitle', '')),
                'start_date': job.get('StartDate', ''),
                'end_date': job.get('EndDate', ''),
                'is_current': job.get('IsCurrent', False),
                'duration_months': job.get('DurationInMonths', 0),
                'job_description': job.get('Description', ''),
                'key_achievements': json.dumps(job.get('Achievements', [])),
                'technologies_used': json.dumps(job.get('Technologies', [])),
                'industry': job.get('Industry', ''),
                'company_size': None,
                'management_experience': job.get('ManagementExperience', {}).get('HasManagementExperience', False),
                'team_size_managed': job.get('ManagementExperience', {}).get('TeamSize', 0),
                'location_city': job.get('Location', {}).get('City', ''),
                'location_country': job.get('Location', {}).get('Country', ''),
                'employment_type': 'full_time'  # Default assumption
            })

        return experience_records

    def _map_education_table(self, resume: Dict, candidate_uuid: str) -> List[Dict]:
        """Map to candidate_education table"""
        education = resume.get('Education', [])
        education_records = []

        for edu in education:
            education_records.append({
                'candidate_uuid': candidate_uuid,
                'institution_name': edu.get('SchoolName', ''),
                'degree_type': edu.get('DegreeType', ''),
                'field_of_study': edu.get('Major', ''),
                'major': edu.get('Major', ''),
                'minor': edu.get('Minor', ''),
                'start_date': edu.get('StartDate', ''),
                'graduation_date': edu.get('EndDate', ''),
                'gpa': edu.get('GPA', {}).get('Score', None),
                'honors': ', '.join(edu.get('Honors', [])),
                'location_city': edu.get('Location', {}).get('City', ''),
                'location_country': edu.get('Location', {}).get('Country', ''),
                'thesis_title': None,
                'relevant_coursework': ', '.join(edu.get('RelevantCoursework', [])),
                'academic_achievements': ', '.join(edu.get('AcademicAchievements', [])),
                'is_highest_degree': edu.get('IsHighestDegree', False),
                'verification_status': 'not_verified'
            })

        return education_records

    def _map_certifications_table(self, resume: Dict, candidate_uuid: str) -> List[Dict]:
        """Map to candidate_certifications table"""
        certifications = resume.get('Certifications', [])
        cert_records = []

        for cert in certifications:
            cert_records.append({
                'candidate_uuid': candidate_uuid,
                'certification_name': cert.get('Name', ''),
                'issuing_organization': cert.get('IssuingOrganization', ''),
                'issue_date': cert.get('EffectiveDate', ''),
                'expiry_date': cert.get('ExpirationDate', ''),
                'credential_id': cert.get('CertificationID', ''),
                'verification_url': cert.get('VerificationUrl', ''),
                'skill_area': cert.get('SkillArea', ''),
                'certification_level': cert.get('Level', ''),
                'is_active': not cert.get('IsExpired', False),
                'renewal_required': cert.get('RequiresRenewal', False),
                'industry_recognition': self._assess_cert_recognition(cert.get('Name', ''))
            })

        return cert_records

    def _map_projects_table(self, resume: Dict, candidate_uuid: str) -> List[Dict]:
        """Map to candidate_projects table"""
        projects = resume.get('Projects', [])
        project_records = []

        for project in projects:
            project_records.append({
                'candidate_uuid': candidate_uuid,
                'project_name': project.get('ProjectName', ''),
                'project_description': project.get('Description', ''),
                'role_in_project': project.get('Role', ''),
                'start_date': project.get('StartDate', ''),
                'end_date': project.get('EndDate', ''),
                'duration_months': project.get('DurationMonths', 0),
                'technologies_used': ', '.join(project.get('Technologies', [])),
                'project_url': project.get('ProjectUrl', ''),
                'github_url': project.get('GitHubUrl', ''),
                'team_size': project.get('TeamSize', 1),
                'project_type': project.get('ProjectType', 'professional'),
                'industry_domain': project.get('IndustryDomain', ''),
                'achievements': project.get('Achievements', ''),
                'challenges_faced': project.get('ChallengesFaced', ''),
                'business_impact': project.get('BusinessImpact', '')
            })

        return project_records

    def _map_languages_table(self, resume: Dict, candidate_uuid: str) -> List[Dict]:
        """Map to candidate_languages table"""
        languages = resume.get('Languages', [])
        language_records = []

        for lang in languages:
            language_records.append({
                'candidate_uuid': candidate_uuid,
                'language_name': lang.get('Language', ''),
                'language_code': lang.get('LanguageCode', ''),
                'proficiency_level': lang.get('FoundDocument', {}).get('ProficiencyLevel', 'conversational'),
                'speaking_level': 'intermediate',  # Default
                'writing_level': 'intermediate',   # Default
                'reading_level': 'intermediate',   # Default
                'is_native': lang.get('Language', '').lower() == 'english',  # Assumption
                'certification_available': False,
                'certification_name': None
            })

        return language_records

    def _map_achievements_table(self, resume: Dict, candidate_uuid: str) -> List[Dict]:
        """Map to candidate_achievements table"""
        achievements = resume.get('Achievements', [])
        achievement_records = []

        for achievement in achievements:
            achievement_records.append({
                'candidate_uuid': candidate_uuid,
                'achievement_title': achievement.get('Title', ''),
                'achievement_description': achievement.get('Description', ''),
                'achievement_type': achievement.get('Type', 'recognition'),
                'date_achieved': achievement.get('Date', ''),
                'issuing_organization': achievement.get('Organization', ''),
                'quantified_result': achievement.get('QuantifiedResult', ''),
                'impact_metrics': achievement.get('ImpactMetrics', ''),
                'context': achievement.get('Context', ''),
                'verification_url': achievement.get('VerificationUrl', ''),
                'industry_relevance': achievement.get('IndustryRelevance', 'medium')
            })

        return achievement_records

    def _map_proficiency_level(self, level: str) -> str:
        """Map proficiency level to Arytic enum"""
        level_mapping = {
            'expert': 'expert',
            'advanced': 'advanced',
            'intermediate': 'intermediate',
            'beginner': 'beginner',
            'novice': 'beginner'
        }
        return level_mapping.get(level.lower(), 'intermediate')

    def _map_seniority_level(self, job_title: str) -> str:
        """Map job title to seniority level"""
        title_lower = job_title.lower()

        if any(word in title_lower for word in ['ceo', 'cto', 'vp', 'director', 'head']):
            return 'executive'
        elif any(word in title_lower for word in ['principal', 'staff', 'lead']):
            return 'principal'
        elif any(word in title_lower for word in ['senior', 'sr']):
            return 'senior'
        elif any(word in title_lower for word in ['junior', 'jr', 'intern']):
            return 'junior'
        else:
            return 'mid'

    def _assess_cert_recognition(self, cert_name: str) -> str:
        """Assess industry recognition of certification"""
        high_recognition = ['aws', 'azure', 'google cloud', 'cisco', 'microsoft', 'oracle', 'salesforce', 'pmp']

        if any(brand in cert_name.lower() for brand in high_recognition):
            return 'high'
        else:
            return 'medium'

    def generate_sql_insert_statements(self, mapped_data: Dict) -> Dict[str, List[str]]:
        """Generate SQL INSERT statements for mapped data"""
        sql_statements = {}

        for table_name, table_data in mapped_data.get('table_data', {}).items():
            statements = []

            if isinstance(table_data, list):
                for record in table_data:
                    if record:  # Skip empty records
                        sql = self._generate_insert_sql(table_name, record)
                        statements.append(sql)
            elif isinstance(table_data, dict) and table_data:
                sql = self._generate_insert_sql(table_name, table_data)
                statements.append(sql)

            sql_statements[table_name] = statements

        return sql_statements

    def _generate_insert_sql(self, table_name: str, record: Dict) -> str:
        """Generate SQL INSERT statement for a single record"""
        fields = list(record.keys())
        values = []

        for field in fields:
            value = record[field]
            if value is None:
                values.append('NULL')
            elif isinstance(value, str):
                # Escape single quotes
                escaped_value = value.replace("'", "''")
                values.append(f"'{escaped_value}'")
            elif isinstance(value, bool):
                values.append('TRUE' if value else 'FALSE')
            else:
                values.append(str(value))

        fields_str = ', '.join(fields)
        values_str = ', '.join(values)

        return f"INSERT INTO {table_name} ({fields_str}) VALUES ({values_str});"

    def export_schema_documentation(self) -> str:
        """Export complete schema documentation"""
        doc = f"""
# Arytic Database Schema Documentation
Generated: {datetime.now().isoformat()}
Version: {self.schema_version}

## Database Tables

"""

        for table_name, schema in self.table_schemas.items():
            doc += f"### {table_name}\n"
            doc += f"Primary Key: {schema['primary_key']}\n"

            if 'foreign_keys' in schema:
                doc += f"Foreign Keys: {schema['foreign_keys']}\n"

            doc += "\n**Fields:**\n"
            for field_name, field_type in schema['fields'].items():
                doc += f"- `{field_name}`: {field_type}\n"

            doc += "\n"

        return doc

# Test the schema mapper
if __name__ == "__main__":
    mapper = AryticSchemaMapper()

    print("🗄️ Arytic Schema Mapper Test")
    print("=" * 50)

    # Sample parsed resume data
    sample_resume = {
        'ContactInformation': {
            'FullName': 'John Michael Smith',
            'FirstName': 'John',
            'MiddleName': 'Michael',
            'LastName': 'Smith',
            'EmailAddresses': [{'EmailAddress': 'john.smith@email.com'}],
            'PhoneNumbers': [{'Raw': '+1-555-123-4567'}],
            'Location': {'City': 'San Francisco', 'State': 'CA', 'Country': 'USA'}
        },
        'Skills': [
            {
                'Name': 'Python',
                'Type': 'Programming',
                'Level': 'Expert',
                'YearsExperience': {'Value': 5},
                'MonthsExperience': 60,
                'LastUsed': '2024-01-01',
                'IsCurrentlyUsing': True
            }
        ],
        'EmploymentHistory': [
            {
                'Employer': 'TechCorp Inc',
                'JobTitle': 'Senior Software Engineer',
                'StartDate': '2022-01-01',
                'EndDate': 'Present',
                'IsCurrent': True,
                'Description': 'Leading development team...'
            }
        ]
    }

    # Test mapping
    mapped_result = mapper.map_to_arytic_schema(sample_resume)
    print(f"✅ Schema mapping completed")
    print(f"📊 Tables mapped: {len(mapped_result.get('table_data', {}))}")

    # Generate SQL statements
    sql_statements = mapper.generate_sql_insert_statements(mapped_result)
    print(f"📝 SQL statements generated for {len(sql_statements)} tables")

    # Export documentation
    documentation = mapper.export_schema_documentation()
    with open('arytic_schema_documentation.md', 'w') as f:
        f.write(documentation)
    print(f"📖 Schema documentation exported")

    print(f"\n🎯 Arytic Schema Mapper ready for enterprise integration!")