#!/usr/bin/env python3
"""
ATS Integration Support
Integrations for Bullhorn, Dice, Ceipal and other ATS systems
"""

import os
import json
import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import base64
import hashlib
import hmac
from urllib.parse import urlencode, quote

from enterprise_resume_parser import EnterpriseResumeParser
from arytic_schema_mapper import AryticSchemaMapper

logger = logging.getLogger(__name__)

class ATSIntegrationBase(ABC):
    """Base class for ATS integrations"""

    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.base_url = config.get('base_url', '')
        self.api_key = config.get('api_key', '')
        self.secret = config.get('secret', '')
        self.session = requests.Session()
        self.access_token = None
        self.token_expires_at = None

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with ATS system"""
        pass

    @abstractmethod
    def create_candidate(self, parsed_resume: Dict) -> Dict:
        """Create candidate in ATS"""
        pass

    @abstractmethod
    def search_candidates(self, criteria: Dict) -> List[Dict]:
        """Search candidates in ATS"""
        pass

    @abstractmethod
    def get_jobs(self, filters: Dict = None) -> List[Dict]:
        """Get job postings from ATS"""
        pass

    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make authenticated request to ATS API"""
        if not self._is_token_valid():
            self.authenticate()

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=30
            )

            if response.status_code in [200, 201]:
                return {'success': True, 'data': response.json()}
            else:
                return {
                    'success': False,
                    'error': f'API Error {response.status_code}: {response.text}',
                    'status_code': response.status_code
                }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _is_token_valid(self) -> bool:
        """Check if access token is valid"""
        if not self.access_token or not self.token_expires_at:
            return False
        return datetime.now() < self.token_expires_at

class BullhornIntegration(ATSIntegrationBase):
    """Bullhorn ATS Integration"""

    def __init__(self, config: Dict[str, str]):
        super().__init__(config)
        self.client_id = config.get('client_id', '')
        self.client_secret = config.get('client_secret', '')
        self.username = config.get('username', '')
        self.password = config.get('password', '')
        self.rest_url = None

    def authenticate(self) -> bool:
        """Authenticate with Bullhorn API"""
        try:
            # Step 1: Get login URL
            auth_url = f"{self.base_url}/oauth/authorize"
            auth_params = {
                'client_id': self.client_id,
                'response_type': 'code',
                'username': self.username,
                'password': self.password,
                'action': 'Login'
            }

            # Step 2: Get access token
            token_url = f"{self.base_url}/oauth/token"
            token_data = {
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'username': self.username,
                'password': self.password
            }

            response = requests.post(token_url, data=token_data)

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                self.rest_url = token_data.get('restUrl')

                # Set token expiration (typically 10 minutes for Bullhorn)
                self.token_expires_at = datetime.now() + timedelta(minutes=9)

                logger.info("✅ Bullhorn authentication successful")
                return True
            else:
                logger.error(f"❌ Bullhorn authentication failed: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Bullhorn authentication error: {e}")
            return False

    def create_candidate(self, parsed_resume: Dict) -> Dict:
        """Create candidate in Bullhorn"""
        try:
            contact_info = parsed_resume.get('ContactInformation', {})
            employment = parsed_resume.get('EmploymentHistory', [])
            skills = parsed_resume.get('Skills', [])

            # Map to Bullhorn candidate format
            candidate_data = {
                'firstName': contact_info.get('FirstName', ''),
                'lastName': contact_info.get('LastName', ''),
                'email': contact_info.get('EmailAddresses', [{}])[0].get('EmailAddress', ''),
                'phone': contact_info.get('PhoneNumbers', [{}])[0].get('Raw', ''),
                'address': self._format_address(contact_info.get('Location', {})),
                'workPhone': contact_info.get('PhoneNumbers', [{}])[1].get('Raw', '') if len(contact_info.get('PhoneNumbers', [])) > 1 else '',
                'skills': ', '.join([skill.get('Name', '') for skill in skills[:10]]),  # Limit to 10 skills
                'status': 'Available',
                'source': 'Resume Parser',
                'comments': f"Parsed resume data - {len(employment)} positions, {len(skills)} skills"
            }

            # Add current position if available
            current_job = next((job for job in employment if job.get('IsCurrent', False)), None)
            if current_job:
                candidate_data['companyName'] = current_job.get('Employer', '')
                candidate_data['occupation'] = current_job.get('JobTitle', '')

            response = self._make_request('POST', 'entity/Candidate', candidate_data)

            if response['success']:
                candidate_id = response['data'].get('changedEntityId')
                logger.info(f"✅ Bullhorn candidate created: ID {candidate_id}")
                return {
                    'success': True,
                    'candidate_id': candidate_id,
                    'ats_system': 'bullhorn'
                }
            else:
                return response

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def search_candidates(self, criteria: Dict) -> List[Dict]:
        """Search candidates in Bullhorn"""
        try:
            # Build search query
            query_parts = []

            if criteria.get('name'):
                query_parts.append(f"name:\"{criteria['name']}\"")
            if criteria.get('email'):
                query_parts.append(f"email:\"{criteria['email']}\"")
            if criteria.get('skills'):
                skills_query = ' OR '.join([f"skills:\"{skill}\"" for skill in criteria['skills']])
                query_parts.append(f"({skills_query})")

            query = ' AND '.join(query_parts) if query_parts else '*'

            params = {
                'query': query,
                'fields': 'id,firstName,lastName,email,phone,companyName,occupation',
                'count': criteria.get('limit', 50),
                'start': criteria.get('offset', 0)
            }

            response = self._make_request('GET', 'search/Candidate', params=params)

            if response['success']:
                candidates = response['data'].get('data', [])
                return {
                    'success': True,
                    'candidates': candidates,
                    'total': response['data'].get('total', 0)
                }
            else:
                return response

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_jobs(self, filters: Dict = None) -> List[Dict]:
        """Get job postings from Bullhorn"""
        try:
            params = {
                'fields': 'id,title,publicDescription,employmentType,dateAdded,isOpen',
                'where': 'isOpen=true',
                'count': filters.get('limit', 100) if filters else 100
            }

            if filters:
                if filters.get('title'):
                    params['where'] += f' AND title LIKE "%{filters["title"]}%"'
                if filters.get('location'):
                    params['where'] += f' AND address.city LIKE "%{filters["location"]}%"'

            response = self._make_request('GET', 'query/JobOrder', params=params)

            if response['success']:
                return {
                    'success': True,
                    'jobs': response['data'].get('data', []),
                    'total': response['data'].get('total', 0)
                }
            else:
                return response

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _format_address(self, location: Dict) -> Dict:
        """Format address for Bullhorn"""
        return {
            'address1': location.get('StreetAddress', ''),
            'city': location.get('City', ''),
            'state': location.get('State', ''),
            'zip': location.get('PostalCode', ''),
            'countryName': location.get('Country', '')
        }

class DiceIntegration(ATSIntegrationBase):
    """Dice ATS Integration"""

    def __init__(self, config: Dict[str, str]):
        super().__init__(config)
        self.client_id = config.get('client_id', '')

    def authenticate(self) -> bool:
        """Authenticate with Dice API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            # Test authentication with a simple API call
            response = requests.get(
                f"{self.base_url}/api/v1/user/profile",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                self.access_token = self.api_key
                self.token_expires_at = datetime.now() + timedelta(hours=1)
                logger.info("✅ Dice authentication successful")
                return True
            else:
                logger.error(f"❌ Dice authentication failed: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Dice authentication error: {e}")
            return False

    def create_candidate(self, parsed_resume: Dict) -> Dict:
        """Create candidate profile in Dice"""
        try:
            contact_info = parsed_resume.get('ContactInformation', {})
            skills = parsed_resume.get('Skills', [])
            employment = parsed_resume.get('EmploymentHistory', [])
            education = parsed_resume.get('Education', [])

            # Map to Dice candidate format
            candidate_data = {
                'personal_info': {
                    'first_name': contact_info.get('FirstName', ''),
                    'last_name': contact_info.get('LastName', ''),
                    'email': contact_info.get('EmailAddresses', [{}])[0].get('EmailAddress', ''),
                    'phone': contact_info.get('PhoneNumbers', [{}])[0].get('Raw', ''),
                    'location': {
                        'city': contact_info.get('Location', {}).get('City', ''),
                        'state': contact_info.get('Location', {}).get('State', ''),
                        'country': contact_info.get('Location', {}).get('Country', '')
                    }
                },
                'skills': [{'name': skill.get('Name', ''), 'level': skill.get('Level', 'intermediate')} for skill in skills[:20]],
                'work_experience': [
                    {
                        'company': job.get('Employer', ''),
                        'title': job.get('JobTitle', ''),
                        'start_date': job.get('StartDate', ''),
                        'end_date': job.get('EndDate', ''),
                        'description': job.get('Description', '')[:500]  # Limit description length
                    }
                    for job in employment[:5]  # Limit to 5 most recent jobs
                ],
                'education': [
                    {
                        'institution': edu.get('SchoolName', ''),
                        'degree': edu.get('DegreeType', ''),
                        'field_of_study': edu.get('Major', ''),
                        'graduation_date': edu.get('EndDate', '')
                    }
                    for edu in education[:3]  # Limit to 3 most recent degrees
                ],
                'source': 'resume_parser'
            }

            response = self._make_request('POST', 'api/v1/candidates', candidate_data)

            if response['success']:
                candidate_id = response['data'].get('id')
                logger.info(f"✅ Dice candidate created: ID {candidate_id}")
                return {
                    'success': True,
                    'candidate_id': candidate_id,
                    'ats_system': 'dice'
                }
            else:
                return response

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def search_candidates(self, criteria: Dict) -> List[Dict]:
        """Search candidates in Dice"""
        try:
            params = {
                'limit': criteria.get('limit', 50),
                'offset': criteria.get('offset', 0)
            }

            if criteria.get('skills'):
                params['skills'] = ','.join(criteria['skills'])
            if criteria.get('location'):
                params['location'] = criteria['location']
            if criteria.get('experience_level'):
                params['experience_level'] = criteria['experience_level']

            response = self._make_request('GET', 'api/v1/candidates/search', params=params)

            if response['success']:
                return {
                    'success': True,
                    'candidates': response['data'].get('candidates', []),
                    'total': response['data'].get('total', 0)
                }
            else:
                return response

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_jobs(self, filters: Dict = None) -> List[Dict]:
        """Get job postings from Dice"""
        try:
            params = {
                'limit': filters.get('limit', 100) if filters else 100,
                'sort': 'date_posted',
                'order': 'desc'
            }

            if filters:
                if filters.get('keyword'):
                    params['q'] = filters['keyword']
                if filters.get('location'):
                    params['location'] = filters['location']
                if filters.get('employment_type'):
                    params['employment_type'] = filters['employment_type']

            response = self._make_request('GET', 'api/v1/jobs', params=params)

            if response['success']:
                return {
                    'success': True,
                    'jobs': response['data'].get('jobs', []),
                    'total': response['data'].get('total', 0)
                }
            else:
                return response

        except Exception as e:
            return {'success': False, 'error': str(e)}

class CeipalIntegration(ATSIntegrationBase):
    """Ceipal ATS Integration"""

    def __init__(self, config: Dict[str, str]):
        super().__init__(config)
        self.tenant_id = config.get('tenant_id', '')

    def authenticate(self) -> bool:
        """Authenticate with Ceipal API"""
        try:
            auth_data = {
                'username': self.config.get('username', ''),
                'password': self.config.get('password', ''),
                'tenant_id': self.tenant_id
            }

            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json=auth_data,
                timeout=10
            )

            if response.status_code == 200:
                auth_response = response.json()
                self.access_token = auth_response.get('access_token')

                # Set token expiration (typically 1 hour for Ceipal)
                self.token_expires_at = datetime.now() + timedelta(minutes=55)

                logger.info("✅ Ceipal authentication successful")
                return True
            else:
                logger.error(f"❌ Ceipal authentication failed: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Ceipal authentication error: {e}")
            return False

    def create_candidate(self, parsed_resume: Dict) -> Dict:
        """Create candidate in Ceipal"""
        try:
            contact_info = parsed_resume.get('ContactInformation', {})
            skills = parsed_resume.get('Skills', [])
            employment = parsed_resume.get('EmploymentHistory', [])

            # Map to Ceipal candidate format
            candidate_data = {
                'first_name': contact_info.get('FirstName', ''),
                'last_name': contact_info.get('LastName', ''),
                'email': contact_info.get('EmailAddresses', [{}])[0].get('EmailAddress', ''),
                'mobile': contact_info.get('PhoneNumbers', [{}])[0].get('Raw', ''),
                'current_location': f"{contact_info.get('Location', {}).get('City', '')}, {contact_info.get('Location', {}).get('State', '')}",
                'skills': [skill.get('Name', '') for skill in skills],
                'source': 'Resume Parser',
                'status': 'Active',
                'tenant_id': self.tenant_id
            }

            # Add current position
            current_job = next((job for job in employment if job.get('IsCurrent', False)), None)
            if current_job:
                candidate_data['current_company'] = current_job.get('Employer', '')
                candidate_data['current_designation'] = current_job.get('JobTitle', '')

            response = self._make_request('POST', 'api/v1/candidates', candidate_data)

            if response['success']:
                candidate_id = response['data'].get('candidate_id')
                logger.info(f"✅ Ceipal candidate created: ID {candidate_id}")
                return {
                    'success': True,
                    'candidate_id': candidate_id,
                    'ats_system': 'ceipal'
                }
            else:
                return response

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def search_candidates(self, criteria: Dict) -> List[Dict]:
        """Search candidates in Ceipal"""
        try:
            search_data = {
                'tenant_id': self.tenant_id,
                'page_size': criteria.get('limit', 50),
                'page_number': (criteria.get('offset', 0) // criteria.get('limit', 50)) + 1
            }

            if criteria.get('skills'):
                search_data['skills'] = criteria['skills']
            if criteria.get('location'):
                search_data['location'] = criteria['location']
            if criteria.get('experience_range'):
                search_data['experience_range'] = criteria['experience_range']

            response = self._make_request('POST', 'api/v1/candidates/search', search_data)

            if response['success']:
                return {
                    'success': True,
                    'candidates': response['data'].get('candidates', []),
                    'total': response['data'].get('total_count', 0)
                }
            else:
                return response

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_jobs(self, filters: Dict = None) -> List[Dict]:
        """Get job postings from Ceipal"""
        try:
            params = {
                'tenant_id': self.tenant_id,
                'status': 'open',
                'page_size': filters.get('limit', 100) if filters else 100
            }

            if filters:
                if filters.get('title'):
                    params['job_title'] = filters['title']
                if filters.get('client'):
                    params['client_name'] = filters['client']

            response = self._make_request('GET', 'api/v1/jobs', params=params)

            if response['success']:
                return {
                    'success': True,
                    'jobs': response['data'].get('jobs', []),
                    'total': response['data'].get('total_count', 0)
                }
            else:
                return response

        except Exception as e:
            return {'success': False, 'error': str(e)}

class ATSIntegrationManager:
    """Manager for all ATS integrations"""

    def __init__(self):
        self.integrations = {}
        self.parser = EnterpriseResumeParser()
        self.schema_mapper = AryticSchemaMapper()

        logger.info("🔗 ATS Integration Manager initialized")

    def add_integration(self, name: str, integration: ATSIntegrationBase):
        """Add an ATS integration"""
        self.integrations[name] = integration
        logger.info(f"➕ Added {name} integration")

    def setup_bullhorn(self, config: Dict[str, str]) -> bool:
        """Setup Bullhorn integration"""
        try:
            integration = BullhornIntegration(config)
            if integration.authenticate():
                self.integrations['bullhorn'] = integration
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Bullhorn setup failed: {e}")
            return False

    def setup_dice(self, config: Dict[str, str]) -> bool:
        """Setup Dice integration"""
        try:
            integration = DiceIntegration(config)
            if integration.authenticate():
                self.integrations['dice'] = integration
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Dice setup failed: {e}")
            return False

    def setup_ceipal(self, config: Dict[str, str]) -> bool:
        """Setup Ceipal integration"""
        try:
            integration = CeipalIntegration(config)
            if integration.authenticate():
                self.integrations['ceipal'] = integration
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Ceipal setup failed: {e}")
            return False

    def sync_candidate_to_ats(self, ats_name: str, resume_text: str) -> Dict:
        """Parse resume and sync to specific ATS"""
        try:
            if ats_name not in self.integrations:
                return {'success': False, 'error': f'ATS {ats_name} not configured'}

            # Parse resume
            parsed_resume = self.parser.parse_resume(resume_text)

            # Create candidate in ATS
            integration = self.integrations[ats_name]
            result = integration.create_candidate(parsed_resume)

            if result['success']:
                # Also map to Arytic schema for local storage
                arytic_data = self.schema_mapper.map_to_arytic_schema(parsed_resume)
                result['arytic_mapping'] = arytic_data

            return result

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def sync_candidate_to_all(self, resume_text: str) -> Dict:
        """Parse resume and sync to all configured ATS systems"""
        results = {}

        # Parse resume once
        parsed_resume = self.parser.parse_resume(resume_text)

        # Sync to all ATS systems
        for ats_name, integration in self.integrations.items():
            try:
                result = integration.create_candidate(parsed_resume)
                results[ats_name] = result
            except Exception as e:
                results[ats_name] = {'success': False, 'error': str(e)}

        return {
            'success': True,
            'parsed_resume': parsed_resume,
            'ats_results': results,
            'total_synced': len([r for r in results.values() if r.get('success', False)])
        }

    def search_across_ats(self, criteria: Dict, ats_systems: List[str] = None) -> Dict:
        """Search candidates across multiple ATS systems"""
        results = {}

        ats_list = ats_systems if ats_systems else list(self.integrations.keys())

        for ats_name in ats_list:
            if ats_name in self.integrations:
                try:
                    result = self.integrations[ats_name].search_candidates(criteria)
                    results[ats_name] = result
                except Exception as e:
                    results[ats_name] = {'success': False, 'error': str(e)}

        return {
            'success': True,
            'search_criteria': criteria,
            'results': results
        }

    def get_integration_status(self) -> Dict:
        """Get status of all integrations"""
        status = {}

        for name, integration in self.integrations.items():
            status[name] = {
                'connected': integration._is_token_valid(),
                'base_url': integration.base_url,
                'token_expires_at': integration.token_expires_at.isoformat() if integration.token_expires_at else None
            }

        return {
            'total_integrations': len(self.integrations),
            'active_integrations': len([s for s in status.values() if s['connected']]),
            'integrations': status
        }

# Test the ATS integrations
if __name__ == "__main__":
    print("🔗 ATS Integration Support Test")
    print("=" * 50)

    manager = ATSIntegrationManager()

    # Sample configurations (would be provided by user)
    sample_configs = {
        'bullhorn': {
            'base_url': 'https://rest.bullhornstaffing.com',
            'client_id': 'your_client_id',
            'client_secret': 'your_client_secret',
            'username': 'your_username',
            'password': 'your_password'
        },
        'dice': {
            'base_url': 'https://api.dice.com',
            'api_key': 'your_api_key',
            'client_id': 'your_client_id'
        },
        'ceipal': {
            'base_url': 'https://api.ceipal.com',
            'username': 'your_username',
            'password': 'your_password',
            'tenant_id': 'your_tenant_id'
        }
    }

    print("📋 Available ATS Systems:")
    for ats_name, config in sample_configs.items():
        print(f"   • {ats_name.title()}: {config['base_url']}")

    print(f"\n🚀 ATS Integration Manager Features:")
    print(f"   • Multi-ATS candidate sync")
    print(f"   • Cross-platform candidate search")
    print(f"   • Resume parsing + ATS integration")
    print(f"   • Arytic schema mapping")
    print(f"   • Authentication management")

    print(f"\n✅ ATS Integration Support ready for enterprise deployment!")

    # Show integration status
    status = manager.get_integration_status()
    print(f"\n📊 Integration Status: {status['active_integrations']}/{status['total_integrations']} active")