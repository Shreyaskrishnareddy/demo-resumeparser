#!/usr/bin/env python3
"""
Skill Experience Duration Tracker
Tracks skill experience duration and last used dates as per BRD requirements
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)

class SkillExperienceTracker:
    def __init__(self):
        """Initialize skill experience tracker"""
        self.skill_patterns = self._build_skill_patterns()
        logger.info("📊 Skill Experience Tracker initialized")

    def _build_skill_patterns(self) -> Dict[str, List[str]]:
        """Build patterns for recognizing skills in text"""
        return {
            'programming': [
                'python', 'java', 'javascript', 'typescript', 'c#', 'c\\+\\+', 'php',
                'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r\\b', 'matlab'
            ],
            'frameworks': [
                'react', 'angular', 'vue', 'django', 'flask', 'spring', 'laravel',
                'express', 'fastapi', 'rails', 'asp\\.net'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
                'oracle', 'sql server', 'cassandra', 'dynamodb'
            ],
            'cloud': [
                'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes',
                'terraform', 'ansible'
            ],
            'tools': [
                'git', 'jenkins', 'jira', 'confluence', 'figma', 'photoshop'
            ]
        }

    def track_skill_experience(self, skills_list: List[str], experience_data: List[Dict]) -> List[Dict]:
        """
        Track experience duration and last used dates for skills

        Args:
            skills_list: List of extracted skills
            experience_data: List of work experience dictionaries

        Returns:
            Enhanced skills list with experience tracking
        """
        enhanced_skills = []

        for skill in skills_list:
            skill_data = {
                'skill_name': skill,
                'total_experience_months': 0,
                'last_used_date': '',
                'experience_breakdown': [],
                'proficiency_level': 'beginner',
                'is_current': False
            }

            # Find skill mentions across all experiences
            skill_experiences = self._find_skill_in_experiences(skill, experience_data)

            if skill_experiences:
                # Calculate total experience and last used
                skill_data = self._calculate_skill_metrics(skill_data, skill_experiences)

            enhanced_skills.append(skill_data)

        return enhanced_skills

    def _find_skill_in_experiences(self, skill: str, experiences: List[Dict]) -> List[Dict]:
        """Find mentions of a skill across work experiences"""
        skill_experiences = []

        for exp in experiences:
            description = exp.get('description', '').lower()
            title = exp.get('title', '').lower()
            company = exp.get('company', '')
            start_date = exp.get('start_date', '')
            end_date = exp.get('end_date', '')

            # Check if skill is mentioned in this experience
            if self._skill_mentioned_in_text(skill, description + ' ' + title):
                skill_exp = {
                    'company': company,
                    'role': exp.get('title', ''),
                    'start_date': start_date,
                    'end_date': end_date,
                    'duration_months': self._calculate_duration_months(start_date, end_date),
                    'context': self._extract_skill_context(skill, description),
                    'usage_intensity': self._assess_usage_intensity(skill, description)
                }
                skill_experiences.append(skill_exp)

        return skill_experiences

    def _skill_mentioned_in_text(self, skill: str, text: str) -> bool:
        """Check if skill is mentioned in text"""
        skill_lower = skill.lower()
        text_lower = text.lower()

        # Direct mention
        if skill_lower in text_lower:
            return True

        # Check for variations and patterns
        skill_patterns = []
        for category, patterns in self.skill_patterns.items():
            skill_patterns.extend(patterns)

        for pattern in skill_patterns:
            if re.search(r'\b' + pattern + r'\b', text_lower, re.IGNORECASE):
                if self._is_skill_match(skill, pattern):
                    return True

        return False

    def _is_skill_match(self, skill: str, pattern: str) -> bool:
        """Check if skill matches a pattern"""
        skill_clean = re.sub(r'[^\w]', '', skill.lower())
        pattern_clean = re.sub(r'[^\w]', '', pattern.lower())

        return skill_clean == pattern_clean or skill_clean in pattern_clean or pattern_clean in skill_clean

    def _extract_skill_context(self, skill: str, description: str) -> str:
        """Extract context around skill mention"""
        skill_lower = skill.lower()
        description_lower = description.lower()

        # Find the position of skill mention
        skill_pos = description_lower.find(skill_lower)
        if skill_pos == -1:
            return ""

        # Extract context (50 chars before and after)
        start = max(0, skill_pos - 50)
        end = min(len(description), skill_pos + len(skill) + 50)

        return description[start:end].strip()

    def _assess_usage_intensity(self, skill: str, description: str) -> str:
        """Assess how intensively the skill was used"""
        description_lower = description.lower()

        high_intensity_indicators = [
            'led', 'architected', 'designed', 'expert', 'mastery', 'advanced',
            'specialized', 'primary', 'core', 'extensive'
        ]

        medium_intensity_indicators = [
            'developed', 'implemented', 'used', 'worked with', 'experience',
            'familiar', 'proficient'
        ]

        if any(indicator in description_lower for indicator in high_intensity_indicators):
            return 'high'
        elif any(indicator in description_lower for indicator in medium_intensity_indicators):
            return 'medium'
        else:
            return 'low'

    def _calculate_duration_months(self, start_date: str, end_date: str) -> int:
        """Calculate duration in months between two dates"""
        try:
            if not start_date:
                return 0

            # Parse start date
            start = self._parse_date_flexible(start_date)
            if not start:
                return 0

            # Parse end date
            if not end_date or any(keyword in end_date.lower() for keyword in ['present', 'current', 'now']):
                end = datetime.now()
            else:
                end = self._parse_date_flexible(end_date)
                if not end:
                    end = datetime.now()

            # Calculate months difference
            if end < start:
                return 0

            delta = relativedelta(end, start)
            return delta.years * 12 + delta.months

        except Exception as e:
            logger.warning(f"Date calculation error: {e}")
            return 0

    def _parse_date_flexible(self, date_str: str) -> Optional[datetime]:
        """Flexibly parse various date formats"""
        if not date_str:
            return None

        # Common date patterns
        patterns = [
            r'(\w+)\s+(\d{4})',  # "Jan 2023"
            r'(\d{1,2})/(\d{4})',  # "01/2023"
            r'(\d{4})',  # "2023"
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # "01/15/2023"
        ]

        for pattern in patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    if len(match.groups()) == 1:  # Year only
                        return datetime(int(match.group(1)), 1, 1)
                    elif len(match.groups()) == 2:  # Month Year
                        month_str, year_str = match.groups()
                        if month_str.isdigit():
                            month = int(month_str)
                        else:
                            month_names = {
                                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                            }
                            month = month_names.get(month_str[:3].lower(), 1)
                        return datetime(int(year_str), month, 1)
                    elif len(match.groups()) == 3:  # Full date
                        month, day, year = match.groups()
                        return datetime(int(year), int(month), int(day))
                except ValueError:
                    continue

        return None

    def _calculate_skill_metrics(self, skill_data: Dict, skill_experiences: List[Dict]) -> Dict:
        """Calculate comprehensive skill metrics"""
        total_months = 0
        latest_end_date = None
        is_current = False

        for exp in skill_experiences:
            months = exp.get('duration_months', 0)
            total_months += months

            # Track latest usage
            end_date_str = exp.get('end_date', '')
            if any(keyword in end_date_str.lower() for keyword in ['present', 'current', 'now']):
                is_current = True
                latest_end_date = datetime.now()
            else:
                parsed_end = self._parse_date_flexible(end_date_str)
                if parsed_end and (not latest_end_date or parsed_end > latest_end_date):
                    latest_end_date = parsed_end

        # Update skill data
        skill_data['total_experience_months'] = total_months
        skill_data['is_current'] = is_current
        skill_data['experience_breakdown'] = skill_experiences

        if latest_end_date:
            skill_data['last_used_date'] = latest_end_date.strftime('%Y-%m-%d')

        # Determine proficiency level
        skill_data['proficiency_level'] = self._determine_proficiency_level(
            total_months, skill_experiences
        )

        return skill_data

    def _determine_proficiency_level(self, total_months: int, experiences: List[Dict]) -> str:
        """Determine proficiency level based on experience"""
        # Base assessment on total months
        if total_months >= 60:  # 5+ years
            base_level = 'expert'
        elif total_months >= 36:  # 3+ years
            base_level = 'advanced'
        elif total_months >= 12:  # 1+ year
            base_level = 'intermediate'
        elif total_months >= 6:  # 6+ months
            base_level = 'beginner_plus'
        else:
            base_level = 'beginner'

        # Adjust based on usage intensity
        high_intensity_count = sum(1 for exp in experiences if exp.get('usage_intensity') == 'high')

        if high_intensity_count >= 2 and base_level in ['intermediate', 'advanced']:
            # Upgrade if multiple high-intensity usages
            level_map = {
                'intermediate': 'advanced',
                'advanced': 'expert'
            }
            return level_map.get(base_level, base_level)

        return base_level

    def generate_skill_summary(self, enhanced_skills: List[Dict]) -> Dict:
        """Generate summary statistics for skills"""
        if not enhanced_skills:
            return {}

        current_skills = [s for s in enhanced_skills if s.get('is_current', False)]
        total_skills = len(enhanced_skills)

        # Group by proficiency
        proficiency_counts = {}
        for skill in enhanced_skills:
            level = skill.get('proficiency_level', 'beginner')
            proficiency_counts[level] = proficiency_counts.get(level, 0) + 1

        # Find most experienced skills
        most_experienced = sorted(
            enhanced_skills,
            key=lambda x: x.get('total_experience_months', 0),
            reverse=True
        )[:5]

        return {
            'total_skills_count': total_skills,
            'current_skills_count': len(current_skills),
            'proficiency_breakdown': proficiency_counts,
            'most_experienced_skills': [
                {
                    'skill': skill['skill_name'],
                    'months': skill.get('total_experience_months', 0),
                    'level': skill.get('proficiency_level', 'beginner')
                }
                for skill in most_experienced
            ],
            'average_experience_months': sum(
                s.get('total_experience_months', 0) for s in enhanced_skills
            ) / total_skills if total_skills > 0 else 0
        }

# Example usage and testing
if __name__ == "__main__":
    tracker = SkillExperienceTracker()

    # Sample data
    skills = ['Python', 'React', 'AWS', 'Docker', 'MySQL']

    experiences = [
        {
            'title': 'Senior Software Engineer',
            'company': 'TechCorp',
            'start_date': 'Jan 2022',
            'end_date': 'Present',
            'description': 'Led development using Python and React. Architected AWS infrastructure with Docker containers.'
        },
        {
            'title': 'Software Developer',
            'company': 'StartupXYZ',
            'start_date': 'Jun 2020',
            'end_date': 'Dec 2021',
            'description': 'Developed web applications using Python Flask and MySQL database. Used Docker for deployment.'
        },
        {
            'title': 'Junior Developer',
            'company': 'FirstJob',
            'start_date': 'Jan 2019',
            'end_date': 'May 2020',
            'description': 'Worked with Python scripts and basic MySQL queries.'
        }
    ]

    print("📊 Skill Experience Tracking Test:")
    print("=" * 50)

    enhanced_skills = tracker.track_skill_experience(skills, experiences)

    for skill in enhanced_skills:
        print(f"\n🎯 {skill['skill_name']}:")
        print(f"   Total Experience: {skill['total_experience_months']} months")
        print(f"   Proficiency: {skill['proficiency_level']}")
        print(f"   Last Used: {skill['last_used_date']}")
        print(f"   Currently Using: {skill['is_current']}")
        print(f"   Experience Count: {len(skill['experience_breakdown'])}")

    print(f"\n📈 Summary:")
    summary = tracker.generate_skill_summary(enhanced_skills)
    print(f"Total Skills: {summary['total_skills_count']}")
    print(f"Current Skills: {summary['current_skills_count']}")
    print(f"Average Experience: {summary['average_experience_months']:.1f} months")