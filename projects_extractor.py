#!/usr/bin/env python3
"""
Projects Extractor for Resume Processing
Extracts project details from both dedicated sections and experience descriptions as per BRD
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class ProjectsExtractor:
    def __init__(self):
        """Initialize the projects extractor"""
        self.project_section_headers = {
            'projects', 'project', 'key projects', 'major projects', 'notable projects',
            'personal projects', 'side projects', 'freelance projects', 'academic projects',
            'research projects', 'open source projects', 'portfolio', 'work samples'
        }

        self.project_indicators = {
            'project', 'built', 'developed', 'created', 'designed', 'implemented',
            'architected', 'led', 'managed', 'delivered', 'launched', 'deployed'
        }

        logger.info("🚀 Projects Extractor initialized")

    def extract_projects_from_text(self, text: str) -> List[Dict]:
        """
        Extract projects from text - required by BRD compliance testing

        Args:
            text: Text content to extract projects from

        Returns:
            List of project dictionaries
        """
        return self.extract_projects(text)

    def extract_projects(self, resume_text: str, experience_data: List[Dict] = None) -> List[Dict]:
        """
        Extract projects from resume text and experience data

        Args:
            resume_text: Full resume text
            experience_data: Parsed experience history

        Returns:
            List of project dictionaries with details
        """
        projects = []

        # Method 1: Extract from dedicated project sections
        dedicated_projects = self._extract_from_project_sections(resume_text)
        projects.extend(dedicated_projects)

        # Method 2: Extract from experience descriptions
        if experience_data:
            experience_projects = self._extract_from_experience(experience_data)
            projects.extend(experience_projects)

        # Method 3: Extract embedded projects from general text
        embedded_projects = self._extract_embedded_projects(resume_text)
        projects.extend(embedded_projects)

        # Remove duplicates and enhance data
        unique_projects = self._deduplicate_projects(projects)
        enhanced_projects = [self._enhance_project_data(proj) for proj in unique_projects]

        return enhanced_projects

    def _extract_from_project_sections(self, text: str) -> List[Dict]:
        """Extract projects from dedicated project sections"""
        projects = []
        lines = text.split('\n')

        # Find project section boundaries
        project_sections = self._find_project_sections(lines)

        for section_start, section_end in project_sections:
            section_text = '\n'.join(lines[section_start:section_end])
            section_projects = self._parse_project_section(section_text)
            projects.extend(section_projects)

        return projects

    def _find_project_sections(self, lines: List[str]) -> List[Tuple[int, int]]:
        """Find the boundaries of project sections"""
        sections = []
        current_section = None

        for i, line in enumerate(lines):
            line_clean = line.strip().lower()

            # Check if line is a project section header
            if self._is_project_header(line_clean):
                if current_section is not None:
                    sections.append((current_section, i))
                current_section = i + 1

            # Check if we've hit another major section (end current project section)
            elif current_section is not None and self._is_major_section_header(line_clean):
                sections.append((current_section, i))
                current_section = None

        # Close last section if needed
        if current_section is not None:
            sections.append((current_section, len(lines)))

        return sections

    def _is_project_header(self, line: str) -> bool:
        """Check if line is a project section header"""
        # Remove common formatting
        clean_line = re.sub(r'[^\w\s]', ' ', line).strip()

        return any(header in clean_line for header in self.project_section_headers)

    def _is_major_section_header(self, line: str) -> bool:
        """Check if line indicates start of a new major section"""
        major_sections = {
            'experience', 'work experience', 'employment', 'employment history',
            'education', 'skills', 'certifications', 'achievements', 'awards',
            'publications', 'references', 'contact', 'summary', 'objective'
        }

        clean_line = re.sub(r'[^\w\s]', ' ', line).strip()
        return any(section in clean_line for section in major_sections)

    def _parse_project_section(self, section_text: str) -> List[Dict]:
        """Parse individual project entries from a project section"""
        projects = []

        # Split by potential project delimiters
        project_blocks = self._split_into_project_blocks(section_text)

        for block in project_blocks:
            project = self._parse_project_block(block)
            if project:
                projects.append(project)

        return projects

    def _split_into_project_blocks(self, text: str) -> List[str]:
        """Split project section into individual project blocks"""
        lines = text.split('\n')
        blocks = []
        current_block = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line starts a new project
            if self._looks_like_project_title(line) and current_block:
                # Save current block and start new one
                blocks.append('\n'.join(current_block))
                current_block = [line]
            else:
                current_block.append(line)

        # Add final block
        if current_block:
            blocks.append('\n'.join(current_block))

        return blocks

    def _looks_like_project_title(self, line: str) -> bool:
        """Check if line looks like a project title"""
        # Project titles often:
        # - Start with a capital letter
        # - Are not too long
        # - Don't contain dates (usually)
        # - May contain project indicators

        if len(line) > 100:
            return False

        # Check for project indicators
        has_indicator = any(indicator in line.lower() for indicator in self.project_indicators)

        # Check formatting patterns
        has_title_format = (
            line[0].isupper() if line else False or
            line.startswith('•') or
            line.startswith('-') or
            line.startswith('*') or
            re.match(r'^\d+\.', line)
        )

        # Avoid lines that look like descriptions
        looks_like_description = (
            len(line.split()) > 15 or
            line.lower().startswith(('responsible for', 'worked on', 'participated in'))
        )

        return (has_indicator or has_title_format) and not looks_like_description

    def _parse_project_block(self, block: str) -> Optional[Dict]:
        """Parse a single project block into structured data"""
        lines = [line.strip() for line in block.split('\n') if line.strip()]

        if not lines:
            return None

        project = {
            'name': '',
            'description': '',
            'company': '',
            'role': '',
            'start_date': '',
            'end_date': '',
            'technologies': [],
            'source': 'dedicated_section'
        }

        # First line is usually the project name
        project['name'] = self._clean_project_name(lines[0])

        # Extract other information from remaining lines
        description_lines = []

        for line in lines[1:]:
            # Check for specific patterns
            if self._extract_dates_from_line(line):
                dates = self._extract_dates_from_line(line)
                if dates:
                    project['start_date'], project['end_date'] = dates

            elif self._extract_role_from_line(line):
                project['role'] = self._extract_role_from_line(line)

            elif self._extract_company_from_line(line):
                project['company'] = self._extract_company_from_line(line)

            elif self._extract_technologies_from_line(line):
                project['technologies'].extend(self._extract_technologies_from_line(line))

            else:
                # Add to description
                description_lines.append(line)

        project['description'] = ' '.join(description_lines).strip()

        # Validate project has minimum required information
        if not project['name'] and not project['description']:
            return None

        return project

    def _extract_from_experience(self, experience_data: List[Dict]) -> List[Dict]:
        """Extract projects mentioned in experience descriptions"""
        projects = []

        for exp in experience_data:
            company = exp.get('company', '')
            role = exp.get('title', '')
            start_date = exp.get('start_date', '')
            end_date = exp.get('end_date', '')
            description = exp.get('description', '')

            # Find project mentions in description
            exp_projects = self._find_projects_in_description(description)

            # Enhance with experience context
            for project in exp_projects:
                project['company'] = project.get('company') or company
                project['role'] = project.get('role') or role
                project['start_date'] = project.get('start_date') or start_date
                project['end_date'] = project.get('end_date') or end_date
                project['source'] = 'experience_description'

            projects.extend(exp_projects)

        return projects

    def _find_projects_in_description(self, description: str) -> List[Dict]:
        """Find project mentions within job descriptions"""
        projects = []

        # Look for explicit project mentions
        project_patterns = [
            r'(?:project|built|developed|created|designed|implemented|launched)\s+([^.!?]+)',
            r'(?:led|managed|delivered)\s+([^.!?]*?project[^.!?]*)',
            r'(?:key\s+)?projects?:\s*([^.!?]+)',
            r'(?:worked on|contributed to|participated in)\s+([^.!?]*?(?:system|platform|application|app|website|tool|service)[^.!?]*)',
            r'(?:responsible for|involved in)\s+([^.!?]*?(?:development|building|creating)[^.!?]*)',
            # Additional more flexible patterns
            r'(?:architected|built|created|developed|designed|implemented|launched|delivered|deployed)\s+(?:a|an|the)?\s*([^.!?]{10,})',
            r'(?:migrated|optimized|enhanced|improved|refactored|modernized)\s+([^.!?]{10,})',
            r'(?:integrated|configured|setup|established|maintained)\s+([^.!?]{10,})',
            r'(?:automated|streamlined|standardized)\s+([^.!?]{10,})',
            # Bullet point patterns
            r'(?:^|\n)\s*[•\-\*]\s*([^.!?\n]{15,})',
            # Action verb patterns
            r'(?:successfully|directly)\s+(?:built|created|developed|implemented|launched|delivered)\s+([^.!?]{10,})',
        ]

        for pattern in project_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                project_desc = match.group(1).strip()
                if len(project_desc) > 3 and not self._is_generic_description(project_desc):  # Even more lenient length filter
                    project = {
                        'name': self._extract_project_name_from_description(project_desc),
                        'description': project_desc,
                        'company': '',
                        'role': '',
                        'start_date': '',
                        'end_date': '',
                        'technologies': self._extract_technologies_from_line(project_desc) or [],
                        'source': 'experience_description'
                    }
                    projects.append(project)

        # Also look for bullet points that describe deliverables/projects
        lines = description.split('\n')
        for line in lines:
            line = line.strip()
            if (line.startswith(('•', '-', '*')) or re.match(r'^\d+\.', line)) and len(line) > 20:
                # Check if line describes a project-like activity
                if any(keyword in line.lower() for keyword in ['built', 'developed', 'created', 'designed', 'implemented', 'delivered', 'launched']):
                    clean_line = re.sub(r'^[\s\-•*\d.]+', '', line).strip()
                    project = {
                        'name': self._extract_project_name_from_description(clean_line),
                        'description': clean_line,
                        'company': '',
                        'role': '',
                        'start_date': '',
                        'end_date': '',
                        'technologies': self._extract_technologies_from_line(clean_line),
                        'source': 'experience_description'
                    }
                    projects.append(project)

        return projects

    def _is_generic_description(self, description: str) -> bool:
        """Check if description is too generic to be a meaningful project"""
        generic_phrases = [
            'various tasks', 'daily tasks', 'general duties', 'routine work',
            'multiple projects', 'different projects', 'various projects',
            'other duties', 'additional responsibilities', 'miscellaneous work',
            'team collaboration', 'regular meetings', 'status updates'
        ]

        description_lower = description.lower()
        return any(phrase in description_lower for phrase in generic_phrases) or len(description.split()) < 3

    def _extract_embedded_projects(self, text: str) -> List[Dict]:
        """Extract projects that might be embedded in other sections"""
        projects = []

        # Look for GitHub/portfolio links that might indicate projects
        github_pattern = r'github\.com/[\w-]+/([\w-]+)'
        portfolio_pattern = r'(?:portfolio|demo|live):\s*([^\s]+)'

        matches = re.finditer(github_pattern, text, re.IGNORECASE)
        for match in matches:
            project_name = match.group(1).replace('-', ' ').replace('_', ' ').title()
            project = {
                'name': project_name,
                'description': f'Open source project: {match.group(0)}',
                'company': '',
                'role': 'Developer',
                'start_date': '',
                'end_date': '',
                'technologies': [],
                'source': 'embedded_link'
            }
            projects.append(project)

        # Also use the same pattern matching as experience extraction for general text
        experience_projects = self._find_projects_in_description(text)
        projects.extend(experience_projects)

        return projects

    def _clean_project_name(self, name: str) -> str:
        """Clean and format project name"""
        # Remove bullet points and numbering
        name = re.sub(r'^[\s\-•*\d.]+', '', name)

        # Remove common prefixes
        name = re.sub(r'^(project|key project|major project):\s*', '', name, flags=re.IGNORECASE)

        return name.strip()

    def _extract_dates_from_line(self, line: str) -> Optional[Tuple[str, str]]:
        """Extract start and end dates from a line"""
        # Common date patterns
        date_patterns = [
            r'(\d{1,2}\/\d{1,2}\/\d{4})\s*-\s*(\d{1,2}\/\d{1,2}\/\d{4})',
            r'(\w+\s+\d{4})\s*-\s*(\w+\s+\d{4})',
            r'(\d{4})\s*-\s*(\d{4})',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1), match.group(2)

        return None

    def _extract_role_from_line(self, line: str) -> Optional[str]:
        """Extract role information from a line"""
        role_patterns = [
            r'(?:role|position|as):\s*([^,\n]+)',
            r'(?:led as|worked as|served as)\s+([^,\n]+)',
        ]

        for pattern in role_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_company_from_line(self, line: str) -> Optional[str]:
        """Extract company information from a line"""
        company_patterns = [
            r'(?:company|client|organization):\s*([^,\n]+)',
            r'(?:at|for)\s+([A-Z][^,\n]*?(?:Inc|LLC|Corp|Ltd|Company))',
        ]

        for pattern in company_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_technologies_from_line(self, line: str) -> List[str]:
        """Extract technologies/tools mentioned in a line"""
        # Common technology keywords
        tech_keywords = {
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node',
            'express', 'django', 'flask', 'spring', 'laravel', 'aws', 'azure',
            'docker', 'kubernetes', 'git', 'mongodb', 'postgresql', 'mysql',
            'redis', 'elasticsearch', 'jenkins', 'ci/cd', 'microservices',
            'api', 'rest', 'graphql', 'websockets', 'html', 'css', 'sass',
            'bootstrap', 'tailwind', 'figma', 'photoshop'
        }

        found_techs = []
        words = re.findall(r'\b\w+\b', line.lower())

        for word in words:
            if word in tech_keywords:
                found_techs.append(word.upper() if len(word) <= 3 else word.title())

        return found_techs

    def _extract_project_name_from_description(self, description: str) -> str:
        """Extract a project name from description text"""
        # Take first few words as project name
        words = description.split()[:4]
        name = ' '.join(words)

        # Clean up
        name = re.sub(r'[^\w\s-]', '', name)
        return name.strip().title()

    def _deduplicate_projects(self, projects: List[Dict]) -> List[Dict]:
        """Remove duplicate projects based on name similarity"""
        unique_projects = []

        for project in projects:
            is_duplicate = False
            project_name = project.get('name', '').lower()

            for existing in unique_projects:
                existing_name = existing.get('name', '').lower()

                # Simple similarity check
                if (project_name in existing_name or existing_name in project_name or
                    self._calculate_name_similarity(project_name, existing_name) > 0.8):

                    # Merge information from duplicate
                    self._merge_project_data(existing, project)
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_projects.append(project)

        return unique_projects

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two project names"""
        if not name1 or not name2:
            return 0.0

        words1 = set(name1.split())
        words2 = set(name2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _merge_project_data(self, existing: Dict, new: Dict):
        """Merge data from a duplicate project into existing project"""
        # Merge descriptions
        if new.get('description') and new['description'] not in existing.get('description', ''):
            existing['description'] = f"{existing.get('description', '')} {new['description']}".strip()

        # Fill missing fields
        for key in ['company', 'role', 'start_date', 'end_date']:
            if not existing.get(key) and new.get(key):
                existing[key] = new[key]

        # Merge technologies
        existing_techs = set(existing.get('technologies', []))
        new_techs = set(new.get('technologies', []))
        existing['technologies'] = list(existing_techs.union(new_techs))

    def _enhance_project_data(self, project: Dict) -> Dict:
        """Enhance project data with additional processing"""
        # Calculate project duration if dates are available
        if project.get('start_date') and project.get('end_date'):
            duration = self._calculate_duration(project['start_date'], project['end_date'])
            project['duration_months'] = duration

        # Estimate project complexity based on description length and technologies
        complexity_score = self._estimate_complexity(project)
        project['complexity_score'] = complexity_score

        # Clean up empty fields
        project = {k: v for k, v in project.items() if v}

        return project

    def _calculate_duration(self, start_date: str, end_date: str) -> int:
        """Calculate project duration in months"""
        try:
            # This is a simplified calculation - could be enhanced for better date parsing
            if 'present' in end_date.lower() or 'current' in end_date.lower():
                end_date = datetime.now().strftime('%Y')

            # Extract years for simple calculation
            start_year = int(re.search(r'\d{4}', start_date).group())
            end_year = int(re.search(r'\d{4}', end_date).group())

            return max(1, (end_year - start_year) * 12)
        except:
            return 1

    def _estimate_complexity(self, project: Dict) -> int:
        """Estimate project complexity (1-10 scale)"""
        score = 1

        # Base score from description length
        desc_len = len(project.get('description', ''))
        if desc_len > 100:
            score += 2
        if desc_len > 200:
            score += 2

        # Add points for technologies
        tech_count = len(project.get('technologies', []))
        score += min(3, tech_count)

        # Add points for management indicators
        desc = project.get('description', '').lower()
        if any(word in desc for word in ['led', 'managed', 'architected', 'designed']):
            score += 2

        return min(10, score)

# Example usage and testing
if __name__ == "__main__":
    extractor = ProjectsExtractor()

    # Test with sample resume text
    sample_text = """
    PROJECTS

    E-Commerce Platform
    Developed a full-stack e-commerce application using React, Node.js, and MongoDB.
    Role: Lead Developer
    Duration: Jan 2023 - Jun 2023
    Technologies: React, Node.js, Express, MongoDB, AWS

    Mobile App for Food Delivery
    Created a cross-platform mobile application using React Native.
    Worked with a team of 4 developers to deliver the app in 3 months.
    Technologies: React Native, Firebase, Redux

    EXPERIENCE

    Software Developer at TechCorp (2022-2023)
    - Built a customer management system using Python and Django
    - Led the development of microservices architecture
    - Implemented CI/CD pipelines using Jenkins and Docker

    """

    print("🚀 Projects Extraction Test:")
    print("=" * 50)

    projects = extractor.extract_projects(sample_text)

    for i, project in enumerate(projects, 1):
        print(f"\n📋 Project {i}:")
        print(f"   Name: {project.get('name', 'N/A')}")
        print(f"   Description: {project.get('description', 'N/A')[:100]}...")
        print(f"   Company: {project.get('company', 'N/A')}")
        print(f"   Role: {project.get('role', 'N/A')}")
        print(f"   Technologies: {', '.join(project.get('technologies', []))}")
        print(f"   Source: {project.get('source', 'N/A')}")
        print(f"   Complexity: {project.get('complexity_score', 'N/A')}/10")