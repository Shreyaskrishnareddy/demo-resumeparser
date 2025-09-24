#!/usr/bin/env python3
"""
Current Job Role Detector
Detects current job role from recent experience as per BRD requirements
"""

import re
from typing import Dict, List, Optional
from datetime import datetime

class CurrentRoleDetector:
    def __init__(self):
        """Initialize current role detector"""
        self.current_indicators = {
            'present', 'current', 'now', 'ongoing', 'till date', 'to date',
            'continuing', 'active'
        }

    def detect_current_role(self, experience_data: List[Dict]) -> Dict[str, str]:
        """
        Detect current job role from experience data

        Args:
            experience_data: List of experience dictionaries

        Returns:
            Dictionary with current role information
        """
        if not experience_data:
            return self._empty_result()

        # Sort experiences by start date (most recent first)
        sorted_experiences = self._sort_by_recency(experience_data)

        # Find current role
        current_role = self._find_current_role(sorted_experiences)

        if current_role:
            return {
                'current_job_role': current_role.get('title', ''),
                'current_company': current_role.get('company', ''),
                'current_start_date': current_role.get('start_date', ''),
                'current_duration': self._calculate_duration(current_role),
                'is_currently_employed': True,
                'role_level': self._assess_role_level(current_role.get('title', '')),
                'employment_status': 'employed'
            }
        else:
            # No current role found, get most recent
            most_recent = sorted_experiences[0] if sorted_experiences else None
            return {
                'current_job_role': most_recent.get('title', '') if most_recent else '',
                'current_company': most_recent.get('company', '') if most_recent else '',
                'current_start_date': most_recent.get('start_date', '') if most_recent else '',
                'current_duration': '',
                'is_currently_employed': False,
                'role_level': self._assess_role_level(most_recent.get('title', '')) if most_recent else '',
                'employment_status': 'between_jobs'
            }

    def _empty_result(self) -> Dict[str, str]:
        """Return empty result structure"""
        return {
            'current_job_role': '',
            'current_company': '',
            'current_start_date': '',
            'current_duration': '',
            'is_currently_employed': False,
            'role_level': '',
            'employment_status': 'unknown'
        }

    def _sort_by_recency(self, experiences: List[Dict]) -> List[Dict]:
        """Sort experiences by recency (most recent first)"""
        def extract_year(date_str: str) -> int:
            if not date_str:
                return 0
            # Extract year from various date formats
            year_match = re.search(r'(\d{4})', str(date_str))
            return int(year_match.group(1)) if year_match else 0

        # Sort by start date descending
        return sorted(experiences,
                     key=lambda x: extract_year(x.get('start_date', '')),
                     reverse=True)

    def _find_current_role(self, experiences: List[Dict]) -> Optional[Dict]:
        """Find the current/active role"""
        for exp in experiences:
            end_date = str(exp.get('end_date', '')).lower().strip()

            # Check for current indicators
            if any(indicator in end_date for indicator in self.current_indicators):
                return exp

            # Check if end date is empty (might indicate current)
            if not end_date or end_date in ['', 'none', 'n/a']:
                return exp

            # Check if end date is recent (within last 6 months)
            if self._is_recent_end_date(end_date):
                return exp

        return None

    def _is_recent_end_date(self, end_date: str) -> bool:
        """Check if end date is recent enough to be considered current"""
        try:
            current_year = datetime.now().year

            # Extract year from end date
            year_match = re.search(r'(\d{4})', end_date)
            if year_match:
                end_year = int(year_match.group(1))
                # Consider current if ended within last year
                return (current_year - end_year) <= 1

            return False
        except:
            return False

    def _calculate_duration(self, experience: Dict) -> str:
        """Calculate duration of current role"""
        start_date = experience.get('start_date', '')
        end_date = experience.get('end_date', '')

        if not start_date:
            return ''

        try:
            # Extract start year
            start_match = re.search(r'(\d{4})', start_date)
            if not start_match:
                return ''

            start_year = int(start_match.group(1))

            # If current role, use current year
            end_date_lower = str(end_date).lower()
            if any(indicator in end_date_lower for indicator in self.current_indicators):
                end_year = datetime.now().year
            else:
                end_match = re.search(r'(\d{4})', str(end_date))
                end_year = int(end_match.group(1)) if end_match else datetime.now().year

            years = end_year - start_year

            if years == 0:
                return "Less than 1 year"
            elif years == 1:
                return "1 year"
            else:
                return f"{years} years"

        except:
            return ''

    def _assess_role_level(self, title: str) -> str:
        """Assess the level/seniority of the role"""
        if not title:
            return 'unknown'

        title_lower = title.lower()

        # Executive level
        executive_indicators = [
            'ceo', 'cto', 'cfo', 'coo', 'vp', 'vice president', 'president',
            'director', 'head of', 'chief'
        ]

        # Senior level
        senior_indicators = [
            'senior', 'sr', 'lead', 'principal', 'staff', 'architect',
            'manager', 'supervisor'
        ]

        # Junior level
        junior_indicators = [
            'junior', 'jr', 'intern', 'trainee', 'associate', 'assistant',
            'entry', 'graduate'
        ]

        if any(indicator in title_lower for indicator in executive_indicators):
            return 'executive'
        elif any(indicator in title_lower for indicator in senior_indicators):
            return 'senior'
        elif any(indicator in title_lower for indicator in junior_indicators):
            return 'junior'
        else:
            return 'mid_level'

# Test the detector
if __name__ == "__main__":
    detector = CurrentRoleDetector()

    # Test with sample experience data
    sample_experiences = [
        {
            'title': 'Senior Software Engineer',
            'company': 'TechCorp Inc',
            'start_date': 'Jan 2022',
            'end_date': 'Present',
            'description': 'Leading development team...'
        },
        {
            'title': 'Software Developer',
            'company': 'StartupXYZ',
            'start_date': 'Jun 2020',
            'end_date': 'Dec 2021',
            'description': 'Developed web applications...'
        },
        {
            'title': 'Junior Developer',
            'company': 'FirstJob Ltd',
            'start_date': 'Jan 2019',
            'end_date': 'May 2020',
            'description': 'Entry level position...'
        }
    ]

    print("👔 Current Role Detection Test:")
    print("=" * 40)

    result = detector.detect_current_role(sample_experiences)

    for key, value in result.items():
        print(f"{key}: {value}")