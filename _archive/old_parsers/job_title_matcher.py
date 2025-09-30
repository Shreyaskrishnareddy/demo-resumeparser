#!/usr/bin/env python3
"""
Job Title Synonym Matching Engine
Implements percentage-based job title family matching as per BRD requirements
"""

import re
import logging
from typing import Dict, List, Tuple, Set
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class JobTitleMatcher:
    def __init__(self):
        """Initialize the job title matching engine"""
        self.job_families = self._build_job_families()
        logger.info("🎯 Job Title Matcher initialized with job families")

    def _build_job_families(self) -> Dict[str, Dict[str, List[str]]]:
        """Build comprehensive job title families and hierarchies"""
        return {
            # Software Engineering
            "software_engineering": {
                "Software Engineer": [
                    "software engineer", "software developer", "software programmer",
                    "application developer", "systems developer", "backend developer",
                    "frontend developer", "full stack developer", "full-stack developer",
                    "software engineer i", "software engineer ii", "software engineer iii",
                    "software engineer 1", "software engineer 2", "software engineer 3",
                    "junior software engineer", "senior software engineer",
                    "software development engineer", "sde", "sde i", "sde ii", "sde iii"
                ],
                "Senior Software Engineer": [
                    "senior software engineer", "senior software developer",
                    "senior application developer", "senior systems developer",
                    "software engineer ii", "software engineer iii", "software engineer 2", "software engineer 3",
                    "senior sde", "sde ii", "sde iii", "lead software engineer"
                ],
                "Software Solutions Engineer": [
                    "software solutions engineer", "solutions engineer",
                    "senior systems engineer", "systems engineer",
                    "technical solutions engineer", "solutions architect"
                ],
                "Full Stack Developer": [
                    "full stack developer", "full-stack developer", "fullstack developer",
                    "full stack engineer", "full-stack engineer", "fullstack engineer"
                ]
            },

            # Data Science & Analytics
            "data_science": {
                "Data Scientist": [
                    "data scientist", "senior data scientist", "junior data scientist",
                    "data analyst", "business analyst", "quantitative analyst",
                    "research scientist", "applied scientist", "ml engineer"
                ],
                "Data Engineer": [
                    "data engineer", "senior data engineer", "big data engineer",
                    "data platform engineer", "etl developer", "data pipeline engineer"
                ],
                "Machine Learning Engineer": [
                    "machine learning engineer", "ml engineer", "ai engineer",
                    "artificial intelligence engineer", "deep learning engineer",
                    "applied scientist", "research engineer"
                ]
            },

            # Product Management
            "product_management": {
                "Product Manager": [
                    "product manager", "senior product manager", "junior product manager",
                    "associate product manager", "product owner", "product lead"
                ],
                "Technical Product Manager": [
                    "technical product manager", "senior technical product manager",
                    "technical pm", "product manager - technical"
                ]
            },

            # DevOps & Infrastructure
            "devops_infrastructure": {
                "DevOps Engineer": [
                    "devops engineer", "senior devops engineer", "devops specialist",
                    "site reliability engineer", "sre", "platform engineer",
                    "infrastructure engineer", "cloud engineer", "systems engineer"
                ],
                "Site Reliability Engineer": [
                    "site reliability engineer", "sre", "senior sre",
                    "reliability engineer", "production engineer"
                ]
            },

            # Quality Assurance
            "quality_assurance": {
                "QA Engineer": [
                    "qa engineer", "quality assurance engineer", "test engineer",
                    "software test engineer", "automation engineer", "sdet",
                    "software development engineer in test", "quality engineer"
                ],
                "Test Automation Engineer": [
                    "test automation engineer", "automation engineer",
                    "senior automation engineer", "qa automation engineer"
                ]
            },

            # Security
            "security": {
                "Security Engineer": [
                    "security engineer", "cybersecurity engineer", "information security engineer",
                    "application security engineer", "network security engineer",
                    "security analyst", "cybersecurity analyst"
                ],
                "Security Architect": [
                    "security architect", "cybersecurity architect",
                    "information security architect", "senior security architect"
                ]
            },

            # Management & Leadership
            "management_leadership": {
                "Engineering Manager": [
                    "engineering manager", "software engineering manager",
                    "technical manager", "development manager", "team lead",
                    "tech lead", "technical lead", "lead engineer"
                ],
                "Technical Lead": [
                    "technical lead", "tech lead", "lead engineer",
                    "senior engineer", "staff engineer", "principal engineer"
                ],
                "Director of Engineering": [
                    "director of engineering", "engineering director",
                    "vp engineering", "vice president engineering"
                ]
            },

            # Design & UX
            "design_ux": {
                "UX Designer": [
                    "ux designer", "user experience designer", "ui/ux designer",
                    "product designer", "interaction designer", "user interface designer"
                ],
                "UI Designer": [
                    "ui designer", "user interface designer", "visual designer",
                    "graphic designer", "web designer"
                ]
            },

            # Business & Strategy
            "business_strategy": {
                "Business Analyst": [
                    "business analyst", "senior business analyst", "junior business analyst",
                    "systems analyst", "process analyst", "functional analyst"
                ],
                "Project Manager": [
                    "project manager", "senior project manager", "program manager",
                    "technical project manager", "it project manager"
                ]
            },

            # Sales & Marketing
            "sales_marketing": {
                "Sales Engineer": [
                    "sales engineer", "technical sales engineer", "solutions engineer",
                    "pre-sales engineer", "sales consultant"
                ],
                "Marketing Manager": [
                    "marketing manager", "digital marketing manager",
                    "product marketing manager", "growth manager"
                ]
            },

            # Operations
            "operations": {
                "Operations Manager": [
                    "operations manager", "business operations manager",
                    "technical operations manager", "it operations manager"
                ],
                "Systems Administrator": [
                    "systems administrator", "system administrator", "sysadmin",
                    "it administrator", "network administrator"
                ]
            }
        }

    def find_job_title_matches(self, candidate_titles: List[str], required_titles: List[str]) -> List[Dict]:
        """
        Find job title matches with percentage scores

        Args:
            candidate_titles: List of job titles from resume
            required_titles: List of required job titles

        Returns:
            List of match results with percentage scores
        """
        matches = []

        for required_title in required_titles:
            best_match = self._find_best_title_match(required_title, candidate_titles)
            if best_match:
                matches.append(best_match)

        return sorted(matches, key=lambda x: x['percentage'], reverse=True)

    def _find_best_title_match(self, required_title: str, candidate_titles: List[str]) -> Dict:
        """Find the best matching job title with percentage score"""
        required_clean = self._clean_title(required_title)
        best_match = None
        best_score = 0

        for candidate_title in candidate_titles:
            candidate_clean = self._clean_title(candidate_title)

            # Check exact match
            if required_clean == candidate_clean:
                return {
                    'required_title': required_title,
                    'matched_title': candidate_title,
                    'percentage': 100,
                    'match_type': 'exact',
                    'family': self._get_title_family(required_title),
                    'seniority_match': self._compare_seniority(required_title, candidate_title)
                }

            # Check family match
            family_score = self._check_title_family_match(required_title, candidate_title)
            if family_score > best_score:
                best_score = family_score
                best_match = {
                    'required_title': required_title,
                    'matched_title': candidate_title,
                    'percentage': family_score,
                    'match_type': 'family',
                    'family': self._get_title_family(required_title),
                    'seniority_match': self._compare_seniority(required_title, candidate_title)
                }

            # Check semantic similarity
            semantic_score = self._calculate_title_similarity(required_clean, candidate_clean)
            if semantic_score > best_score and semantic_score >= 70:  # Minimum threshold
                best_score = semantic_score
                best_match = {
                    'required_title': required_title,
                    'matched_title': candidate_title,
                    'percentage': semantic_score,
                    'match_type': 'semantic',
                    'family': None,
                    'seniority_match': self._compare_seniority(required_title, candidate_title)
                }

        return best_match if best_score >= 70 else None

    def _check_title_family_match(self, required_title: str, candidate_title: str) -> int:
        """Check if job titles belong to the same family and calculate percentage"""
        required_clean = self._clean_title(required_title)
        candidate_clean = self._clean_title(candidate_title)

        for category, families in self.job_families.items():
            for main_title, synonyms in families.items():
                # Check if both titles are in the same family
                required_in_family = (required_clean == main_title.lower() or
                                    any(required_clean == syn.lower() for syn in synonyms))
                candidate_in_family = (candidate_clean == main_title.lower() or
                                     any(candidate_clean == syn.lower() for syn in synonyms))

                if required_in_family and candidate_in_family:
                    return self._calculate_title_family_percentage(
                        required_title, candidate_title, main_title, synonyms)

        return 0

    def _calculate_title_family_percentage(self, required: str, candidate: str,
                                         main_title: str, synonyms: List[str]) -> int:
        """Calculate percentage match within job title family"""
        required_clean = self._clean_title(required)
        candidate_clean = self._clean_title(candidate)
        main_title_lower = main_title.lower()

        # Both are main title
        if required_clean == main_title_lower and candidate_clean == main_title_lower:
            return 100

        # One is main title, other is synonym
        if required_clean == main_title_lower or candidate_clean == main_title_lower:
            seniority_adjustment = self._get_seniority_adjustment(required, candidate)
            return max(90 + seniority_adjustment, 85)

        # Both are synonyms - check seniority levels
        seniority_match = self._compare_seniority(required, candidate)
        base_score = 85

        if seniority_match == "exact":
            return 95
        elif seniority_match == "close":
            return 90
        elif seniority_match == "different":
            return max(base_score - 10, 75)

        return base_score

    def _compare_seniority(self, title1: str, title2: str) -> str:
        """Compare seniority levels between job titles"""
        seniority1 = self._extract_seniority_level(title1)
        seniority2 = self._extract_seniority_level(title2)

        if seniority1 == seniority2:
            return "exact"
        elif abs(seniority1 - seniority2) <= 1:
            return "close"
        else:
            return "different"

    def _extract_seniority_level(self, title: str) -> int:
        """Extract seniority level from job title (0=junior, 1=mid, 2=senior, 3=lead, 4=principal)"""
        title_lower = title.lower()

        # Principal/Staff level
        if any(word in title_lower for word in ["principal", "staff", "distinguished", "chief"]):
            return 4

        # Lead/Director level
        if any(word in title_lower for word in ["lead", "director", "vp", "vice president", "head of"]):
            return 3

        # Senior level
        if any(word in title_lower for word in ["senior", "sr", "iii", " 3"]):
            return 2

        # Junior level
        if any(word in title_lower for word in ["junior", "jr", "associate", "i", " 1"]):
            return 0

        # Default to mid-level
        return 1

    def _get_seniority_adjustment(self, title1: str, title2: str) -> int:
        """Get seniority adjustment for percentage calculation"""
        level1 = self._extract_seniority_level(title1)
        level2 = self._extract_seniority_level(title2)

        diff = abs(level1 - level2)
        if diff == 0:
            return 5  # Same level
        elif diff == 1:
            return 0  # Adjacent level
        else:
            return -5  # Different levels

    def _calculate_title_similarity(self, title1: str, title2: str) -> int:
        """Calculate semantic similarity between job titles"""
        # Use SequenceMatcher for basic similarity
        ratio = SequenceMatcher(None, title1, title2).ratio()

        # Check for common patterns and abbreviations
        if self._check_title_patterns(title1, title2):
            ratio = max(ratio, 0.8)

        # Adjust for common title variations
        if self._are_related_titles(title1, title2):
            ratio = max(ratio, 0.78)  # Increased from 0.75 to 0.78

        # Special handling for specific high-similarity pairs
        if self._are_high_similarity_pair(title1, title2):
            ratio = max(ratio, 0.80)

        return int(ratio * 100)

    def _check_title_patterns(self, title1: str, title2: str) -> bool:
        """Check for common job title patterns and abbreviations"""
        patterns = [
            (r'software engineer', r'sde'),
            (r'product manager', r'pm'),
            (r'technical lead', r'tech lead'),
            (r'site reliability engineer', r'sre'),
            (r'quality assurance', r'qa'),
            (r'user experience', r'ux'),
            (r'user interface', r'ui'),
            (r'machine learning', r'ml'),
            (r'artificial intelligence', r'ai'),
            (r'full stack', r'fullstack'),
            (r'full-stack', r'fullstack')
        ]

        for long_form, short_form in patterns:
            if ((long_form in title1 and short_form in title2) or
                (short_form in title1 and long_form in title2)):
                return True

        return False

    def _are_related_titles(self, title1: str, title2: str) -> bool:
        """Check if titles are related but not in same family"""
        related_groups = [
            ["engineer", "developer", "programmer"],
            ["manager", "lead", "director"],
            ["analyst", "specialist", "consultant"],
            ["designer", "architect"],
            ["administrator", "operator"]
        ]

        for group in related_groups:
            in_group1 = any(word in title1.lower() for word in group)
            in_group2 = any(word in title2.lower() for word in group)
            if in_group1 and in_group2:
                return True

        return False

    def _are_high_similarity_pair(self, title1: str, title2: str) -> bool:
        """Check for specific high-similarity pairs that should score >75%"""
        title1_lower = title1.lower()
        title2_lower = title2.lower()

        high_similarity_pairs = [
            ("software engineer", "software developer"),
            ("software developer", "software engineer"),
            ("data scientist", "data analyst"),
            ("data analyst", "data scientist"),
            ("product manager", "project manager"),
            ("project manager", "product manager"),
            ("frontend developer", "front end developer"),
            ("backend developer", "back end developer"),
            ("full stack developer", "fullstack developer"),
        ]

        for pair1, pair2 in high_similarity_pairs:
            if (pair1 in title1_lower and pair2 in title2_lower) or (pair2 in title1_lower and pair1 in title2_lower):
                return True

        return False

    def _clean_title(self, title: str) -> str:
        """Clean and normalize job title"""
        # Remove common company-specific suffixes
        title = re.sub(r'\s*-\s*(remote|contract|freelance|intern|internship).*$', '', title, flags=re.IGNORECASE)
        # Remove special characters except spaces and hyphens
        title = re.sub(r'[^\w\s\-/]', '', title)
        # Normalize whitespace and convert to lowercase
        return ' '.join(title.lower().split())

    def _get_title_family(self, title: str) -> str:
        """Get the family category for a job title"""
        title_clean = self._clean_title(title)

        for category, families in self.job_families.items():
            for main_title, synonyms in families.items():
                if (title_clean == main_title.lower() or
                    any(title_clean == syn.lower() for syn in synonyms)):
                    return category

        return "general"

    def get_title_suggestions(self, partial_title: str, limit: int = 5) -> List[str]:
        """Get job title suggestions based on partial input"""
        partial_clean = self._clean_title(partial_title)
        suggestions = []

        for category, families in self.job_families.items():
            for main_title, synonyms in families.items():
                # Check main title
                if partial_clean in main_title.lower():
                    suggestions.append(main_title)

                # Check synonyms
                for synonym in synonyms:
                    if partial_clean in synonym.lower():
                        suggestions.append(synonym)

        return list(set(suggestions))[:limit]

    def classify_job_family(self, job_title: str) -> str:
        """
        Classify a job title into its family category
        Required by BRD compliance testing

        Args:
            job_title: Job title to classify

        Returns:
            Family classification string (e.g., "software_engineering")
        """
        family = self._get_title_family(job_title)

        # Convert underscore format to space format for test compatibility
        if family == "software_engineering":
            return "software engineering"
        elif family == "data_science":
            return "data science"
        elif family == "product_management":
            return "product management"
        elif family == "devops_infrastructure":
            return "devops infrastructure"
        elif family == "quality_assurance":
            return "quality assurance"
        elif family == "management_leadership":
            return "management leadership"
        elif family == "design_ux":
            return "design ux"
        elif family == "business_strategy":
            return "business strategy"
        elif family == "sales_marketing":
            return "sales marketing"
        else:
            return family.replace("_", " ") if "_" in family else family

    def extract_seniority_level(self, job_title: str) -> int:
        """
        Extract seniority level from job title
        Required by BRD compliance testing

        Args:
            job_title: Job title to analyze

        Returns:
            Seniority level (0=junior, 1=mid, 2=senior, 3=lead, 4=principal)
        """
        return self._extract_seniority_level(job_title)

    def calculate_title_similarity(self, title1: str, title2: str) -> int:
        """
        Calculate semantic similarity between job titles
        Required by BRD compliance testing

        Args:
            title1: First job title
            title2: Second job title

        Returns:
            Similarity percentage (0-100)
        """
        title1_clean = self._clean_title(title1)
        title2_clean = self._clean_title(title2)
        return self._calculate_title_similarity(title1_clean, title2_clean)

    def analyze_title_coverage(self, candidate_titles: List[str], required_titles: List[str]) -> Dict:
        """Analyze overall job title coverage"""
        matches = self.find_job_title_matches(candidate_titles, required_titles)

        total_required = len(required_titles)
        matched_titles = len(matches)

        # Calculate weighted score based on match percentages
        if matches:
            weighted_score = sum(match['percentage'] for match in matches) / total_required
        else:
            weighted_score = 0

        coverage_percentage = (matched_titles / total_required) * 100 if total_required > 0 else 0

        return {
            'total_required_titles': total_required,
            'matched_titles': matched_titles,
            'coverage_percentage': round(coverage_percentage, 2),
            'weighted_score': round(weighted_score, 2),
            'matches': matches,
            'missing_titles': [title for title in required_titles
                             if not any(match['required_title'] == title for match in matches)]
        }

# Example usage and testing
if __name__ == "__main__":
    matcher = JobTitleMatcher()

    # Test case from BRD: Software Solutions Engineer vs Senior Systems Engineer
    candidate_titles = ["Software Solutions Engineer", "Full Stack Developer", "Technical Lead"]
    required_titles = ["Senior Systems Engineer", "Software Engineer", "Engineering Manager"]

    print("🔍 Job Title Matching Analysis:")
    print("=" * 50)

    analysis = matcher.analyze_title_coverage(candidate_titles, required_titles)

    print(f"📊 Coverage: {analysis['coverage_percentage']}%")
    print(f"🎯 Weighted Score: {analysis['weighted_score']}")
    print("\n📋 Detailed Matches:")

    for match in analysis['matches']:
        print(f"  ✅ {match['required_title']} → {match['matched_title']} ({match['percentage']}%)")
        print(f"     Type: {match['match_type']}, Family: {match['family']}")
        print(f"     Seniority: {match['seniority_match']}")

    print(f"\n❌ Missing Titles: {', '.join(analysis['missing_titles'])}")