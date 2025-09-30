#!/usr/bin/env python3
"""
Skill Synonym Matching Engine
Implements percentage-based semantic similarity for skill matching as per BRD requirements
"""

import re
import logging
from typing import Dict, List, Tuple, Set
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class SkillSynonymMatcher:
    def __init__(self):
        """Initialize the skill synonym matching engine"""
        self.skill_families = self._build_skill_families()
        logger.info("🎯 Skill Synonym Matcher initialized with skill families")

    def _build_skill_families(self) -> Dict[str, Dict[str, List[str]]]:
        """Build comprehensive skill families and synonyms"""
        return {
            # Programming Languages
            "programming_languages": {
                "JavaScript": ["js", "javascript", "ecmascript", "node", "nodejs", "node.js"],
                "Python": ["python", "py", "python3", "python2"],
                "Java": ["java", "openjdk", "oracle java"],
                "C#": ["c#", "csharp", "c-sharp", ".net", "dotnet"],
                "C++": ["c++", "cpp", "c plus plus"],
                "C": ["c programming", "c language"],
                "PHP": ["php", "php7", "php8"],
                "Ruby": ["ruby", "ruby on rails", "ror"],
                "Go": ["golang", "go", "go lang"],
                "Rust": ["rust", "rust lang"],
                "Swift": ["swift", "swift ui", "swiftui"],
                "Kotlin": ["kotlin", "kotlin android"],
                "TypeScript": ["typescript", "ts"],
                "Scala": ["scala", "scala programming"],
                "R": ["r programming", "r language", "r statistical"],
                "MATLAB": ["matlab", "octave"],
                "Perl": ["perl", "perl5"],
                "Shell": ["bash", "shell", "shell scripting", "zsh", "fish"]
            },

            # Frontend Frameworks
            "frontend_frameworks": {
                "React": ["react", "reactjs", "react.js", "react native", "react-native"],
                "Angular": ["angular", "angularjs", "angular 2", "angular 4", "angular 5",
                           "angular 6", "angular 7", "angular 8", "angular 9", "angular 10",
                           "angular 11", "angular 12", "angular 13", "angular 14", "angular 15", "angular 16"],
                "Vue": ["vue", "vuejs", "vue.js", "vue 2", "vue 3", "nuxt", "nuxtjs"],
                "Svelte": ["svelte", "sveltekit"],
                "Ember": ["ember", "emberjs", "ember.js"],
                "jQuery": ["jquery", "jquery ui"],
                "Bootstrap": ["bootstrap", "bootstrap 3", "bootstrap 4", "bootstrap 5"],
                "Tailwind": ["tailwind", "tailwindcss", "tailwind css"]
            },

            # Backend Frameworks
            "backend_frameworks": {
                "Express": ["express", "expressjs", "express.js"],
                "Django": ["django", "django rest", "django rest framework", "drf"],
                "Flask": ["flask", "flask-restful"],
                "FastAPI": ["fastapi", "fast api"],
                "Spring": ["spring", "spring boot", "spring framework", "spring mvc"],
                "Laravel": ["laravel", "laravel 8", "laravel 9"],
                "CodeIgniter": ["codeigniter", "ci"],
                "Symfony": ["symfony", "symfony 5", "symfony 6"],
                "Rails": ["rails", "ruby on rails", "ror"],
                "ASP.NET": ["asp.net", "asp net", "aspnet", ".net core", "dotnet core"]
            },

            # Databases
            "databases": {
                "MySQL": ["mysql", "mysql 5", "mysql 8", "mariadb"],
                "PostgreSQL": ["postgresql", "postgres", "psql"],
                "MongoDB": ["mongodb", "mongo", "mongoose"],
                "SQLite": ["sqlite", "sqlite3"],
                "Redis": ["redis", "redis cache"],
                "Elasticsearch": ["elasticsearch", "elastic search", "es"],
                "Oracle": ["oracle", "oracle db", "oracle database"],
                "SQL Server": ["sql server", "mssql", "microsoft sql server"],
                "Cassandra": ["cassandra", "apache cassandra"],
                "DynamoDB": ["dynamodb", "dynamo db", "amazon dynamodb"]
            },

            # Cloud Platforms
            "cloud_platforms": {
                "AWS": ["aws", "amazon web services", "amazon aws", "ec2", "s3", "lambda"],
                "Azure": ["azure", "microsoft azure", "azure cloud"],
                "GCP": ["gcp", "google cloud", "google cloud platform"],
                "DigitalOcean": ["digitalocean", "digital ocean"],
                "Heroku": ["heroku", "heroku cloud"],
                "Vercel": ["vercel", "zeit now"],
                "Netlify": ["netlify", "netlify deploy"]
            },

            # DevOps Tools
            "devops_tools": {
                "Docker": ["docker", "docker container", "containerization"],
                "Kubernetes": ["kubernetes", "k8s", "kubectl"],
                "Jenkins": ["jenkins", "jenkins ci", "jenkins pipeline"],
                "GitLab CI": ["gitlab ci", "gitlab", "gitlab pipeline"],
                "GitHub Actions": ["github actions", "gh actions"],
                "Ansible": ["ansible", "ansible playbook"],
                "Terraform": ["terraform", "tf"],
                "Vagrant": ["vagrant", "vagrant box"],
                "Chef": ["chef", "chef cookbook"],
                "Puppet": ["puppet", "puppet master"]
            },

            # Testing Frameworks
            "testing_frameworks": {
                "Jest": ["jest", "jest testing"],
                "Mocha": ["mocha", "mocha js"],
                "Cypress": ["cypress", "cypress io"],
                "Selenium": ["selenium", "selenium webdriver"],
                "Pytest": ["pytest", "py.test"],
                "JUnit": ["junit", "junit 4", "junit 5"],
                "TestNG": ["testng", "test ng"],
                "Jasmine": ["jasmine", "jasmine js"],
                "Karma": ["karma", "karma runner"],
                "Puppeteer": ["puppeteer", "headless chrome"]
            },

            # Mobile Development
            "mobile_frameworks": {
                "React Native": ["react native", "react-native", "rn"],
                "Flutter": ["flutter", "dart flutter"],
                "Ionic": ["ionic", "ionic framework"],
                "Xamarin": ["xamarin", "xamarin forms"],
                "Cordova": ["cordova", "phonegap"],
                "NativeScript": ["nativescript", "native script"]
            },

            # Version Control
            "version_control": {
                "Git": ["git", "github", "gitlab", "bitbucket"],
                "SVN": ["svn", "subversion", "apache subversion"],
                "Mercurial": ["mercurial", "hg"]
            },

            # Design Tools
            "design_tools": {
                "Figma": ["figma", "figma design"],
                "Sketch": ["sketch", "sketch app"],
                "Adobe XD": ["adobe xd", "xd", "experience design"],
                "Photoshop": ["photoshop", "adobe photoshop", "ps"],
                "Illustrator": ["illustrator", "adobe illustrator", "ai"],
                "InVision": ["invision", "invision app"]
            }
        }

    def find_skill_matches(self, candidate_skills: List[str], required_skills: List[str]) -> List[Dict]:
        """
        Find skill matches with percentage scores

        Args:
            candidate_skills: List of skills from resume
            required_skills: List of required skills for job

        Returns:
            List of match results with percentage scores
        """
        matches = []

        for required_skill in required_skills:
            best_match = self._find_best_match(required_skill, candidate_skills)
            if best_match:
                matches.append(best_match)

        return sorted(matches, key=lambda x: x['percentage'], reverse=True)

    def _find_best_match(self, required_skill: str, candidate_skills: List[str]) -> Dict:
        """Find the best matching skill with percentage score"""
        required_clean = self._clean_skill(required_skill)
        best_match = None
        best_score = 0

        for candidate_skill in candidate_skills:
            candidate_clean = self._clean_skill(candidate_skill)

            # Check exact match
            if required_clean == candidate_clean:
                return {
                    'required_skill': required_skill,
                    'matched_skill': candidate_skill,
                    'percentage': 100,
                    'similarity_percentage': 100,
                    'match_type': 'exact',
                    'family': self._get_skill_family(required_skill)
                }

            # Check family match
            family_score = self._check_family_match(required_skill, candidate_skill)
            if family_score > best_score:
                best_score = family_score
                best_match = {
                    'required_skill': required_skill,
                    'matched_skill': candidate_skill,
                    'percentage': family_score,
                    'similarity_percentage': family_score,
                    'match_type': 'family',
                    'family': self._get_skill_family(required_skill)
                }

            # Check semantic similarity
            semantic_score = self._calculate_semantic_similarity(required_clean, candidate_clean)
            if semantic_score > best_score and semantic_score >= 70:  # Minimum threshold
                best_score = semantic_score
                best_match = {
                    'required_skill': required_skill,
                    'matched_skill': candidate_skill,
                    'percentage': semantic_score,
                    'similarity_percentage': semantic_score,
                    'match_type': 'semantic',
                    'family': None
                }

        return best_match if best_score >= 70 else None

    def _check_family_match(self, required_skill: str, candidate_skill: str) -> int:
        """Check if skills belong to the same family and calculate percentage"""
        required_clean = self._clean_skill(required_skill)
        candidate_clean = self._clean_skill(candidate_skill)

        for category, families in self.skill_families.items():
            for main_skill, synonyms in families.items():
                # Check if both skills are in the same family
                required_in_family = (required_clean == main_skill.lower() or
                                    any(required_clean == syn.lower() for syn in synonyms))
                candidate_in_family = (candidate_clean == main_skill.lower() or
                                     any(candidate_clean == syn.lower() for syn in synonyms))

                if required_in_family and candidate_in_family:
                    return self._calculate_family_percentage(required_clean, candidate_clean, main_skill, synonyms)

        return 0

    def _calculate_family_percentage(self, required: str, candidate: str, main_skill: str, synonyms: List[str]) -> int:
        """Calculate percentage match within skill family"""
        main_skill_lower = main_skill.lower()

        # Both are main skill name
        if required == main_skill_lower and candidate == main_skill_lower:
            return 100

        # One is main skill, other is synonym
        if required == main_skill_lower or candidate == main_skill_lower:
            return 95

        # Both are synonyms - check if they're version variants
        if self._are_version_variants(required, candidate):
            return self._calculate_version_similarity(required, candidate)

        # Both are synonyms but different types
        return 85

    def _are_version_variants(self, skill1: str, skill2: str) -> bool:
        """Check if skills are version variants (e.g., Angular 11 vs Angular 12)"""
        # Extract version numbers
        version1 = re.search(r'(\d+(?:\.\d+)*)', skill1)
        version2 = re.search(r'(\d+(?:\.\d+)*)', skill2)

        if version1 and version2:
            base1 = re.sub(r'\s*\d+(?:\.\d+)*\s*', '', skill1).strip()
            base2 = re.sub(r'\s*\d+(?:\.\d+)*\s*', '', skill2).strip()
            return base1 == base2

        return False

    def _calculate_version_similarity(self, skill1: str, skill2: str) -> int:
        """Calculate similarity between version variants"""
        version1 = re.search(r'(\d+(?:\.\d+)*)', skill1)
        version2 = re.search(r'(\d+(?:\.\d+)*)', skill2)

        if version1 and version2:
            v1_parts = [int(x) for x in version1.group(1).split('.')]
            v2_parts = [int(x) for x in version2.group(1).split('.')]

            # Calculate version distance
            major_diff = abs(v1_parts[0] - v2_parts[0]) if len(v1_parts) > 0 and len(v2_parts) > 0 else 0

            if major_diff == 0:
                return 98  # Same major version
            elif major_diff == 1:
                return 95  # Adjacent major version
            elif major_diff == 2:
                return 90  # Two versions apart
            else:
                return max(85 - (major_diff - 2) * 5, 75)  # Decreasing similarity

        return 85

    def _calculate_semantic_similarity(self, skill1: str, skill2: str) -> int:
        """Calculate semantic similarity using string matching"""
        # Use SequenceMatcher for basic similarity
        ratio = SequenceMatcher(None, skill1, skill2).ratio()

        # Check for common abbreviations and patterns
        if self._check_common_patterns(skill1, skill2):
            ratio = max(ratio, 0.8)

        return int(ratio * 100)

    def _check_common_patterns(self, skill1: str, skill2: str) -> bool:
        """Check for common skill abbreviation patterns"""
        patterns = [
            (r'javascript', r'js'),
            (r'typescript', r'ts'),
            (r'kubernetes', r'k8s'),
            (r'postgresql', r'postgres'),
            (r'mongodb', r'mongo'),
            (r'artificial intelligence', r'ai'),
            (r'machine learning', r'ml'),
            (r'natural language processing', r'nlp'),
            (r'continuous integration', r'ci'),
            (r'continuous deployment', r'cd')
        ]

        for long_form, short_form in patterns:
            if ((long_form in skill1 and short_form in skill2) or
                (short_form in skill1 and long_form in skill2)):
                return True

        return False

    def _clean_skill(self, skill: str) -> str:
        """Clean and normalize skill name"""
        return re.sub(r'[^\w\s.]', '', skill.lower().strip())

    def _get_skill_family(self, skill: str) -> str:
        """Get the family category for a skill"""
        skill_clean = self._clean_skill(skill)

        for category, families in self.skill_families.items():
            for main_skill, synonyms in families.items():
                if (skill_clean == main_skill.lower() or
                    any(skill_clean == syn.lower() for syn in synonyms)):
                    return category

        return "general"

    def get_skill_suggestions(self, partial_skill: str, limit: int = 5) -> List[str]:
        """Get skill suggestions based on partial input"""
        partial_clean = self._clean_skill(partial_skill)
        suggestions = []

        for category, families in self.skill_families.items():
            for main_skill, synonyms in families.items():
                # Check main skill
                if partial_clean in main_skill.lower():
                    suggestions.append(main_skill)

                # Check synonyms
                for synonym in synonyms:
                    if partial_clean in synonym.lower():
                        suggestions.append(synonym)

        return list(set(suggestions))[:limit]

    def calculate_skill_similarity(self, skill1: str, skill2: str) -> float:
        """
        Calculate similarity percentage between two skills
        Required by BRD compliance testing

        Args:
            skill1: First skill to compare
            skill2: Second skill to compare

        Returns:
            Similarity percentage as float (0.0 to 100.0)
        """
        # Check family match first
        family_score = self._check_family_match(skill1, skill2)
        if family_score > 0:
            return float(family_score)

        # Fall back to semantic similarity
        skill1_clean = self._clean_skill(skill1)
        skill2_clean = self._clean_skill(skill2)
        semantic_score = self._calculate_semantic_similarity(skill1_clean, skill2_clean)

        return float(semantic_score)

    def match_skills_bulk(self, candidate_skills: List[str], required_skills: List[str]) -> List[Dict]:
        """
        Bulk skill matching method required by BRD compliance testing

        Args:
            candidate_skills: List of candidate skills
            required_skills: List of required skills

        Returns:
            List of skill match results
        """
        return self.find_skill_matches(candidate_skills, required_skills)

    def analyze_skill_coverage(self, candidate_skills: List[str], required_skills: List[str]) -> Dict:
        """Analyze overall skill coverage"""
        matches = self.find_skill_matches(candidate_skills, required_skills)

        total_required = len(required_skills)
        matched_skills = len(matches)

        # Calculate weighted score based on match percentages
        if matches:
            weighted_score = sum(match['percentage'] for match in matches) / total_required
        else:
            weighted_score = 0

        coverage_percentage = (matched_skills / total_required) * 100 if total_required > 0 else 0

        return {
            'total_required_skills': total_required,
            'matched_skills': matched_skills,
            'coverage_percentage': round(coverage_percentage, 2),
            'weighted_score': round(weighted_score, 2),
            'matches': matches,
            'missing_skills': [skill for skill in required_skills
                             if not any(match['required_skill'] == skill for match in matches)]
        }

# Example usage and testing
if __name__ == "__main__":
    matcher = SkillSynonymMatcher()

    # Test case from BRD: Angular versions
    candidate_skills = ["Angular 11", "React", "Node.js", "MongoDB", "AWS"]
    required_skills = ["Angular 12", "React Native", "Express", "PostgreSQL", "Azure"]

    print("🔍 Skill Matching Analysis:")
    print("=" * 50)

    analysis = matcher.analyze_skill_coverage(candidate_skills, required_skills)

    print(f"📊 Coverage: {analysis['coverage_percentage']}%")
    print(f"🎯 Weighted Score: {analysis['weighted_score']}")
    print("\n📋 Detailed Matches:")

    for match in analysis['matches']:
        print(f"  ✅ {match['required_skill']} → {match['matched_skill']} ({match['percentage']}%)")
        print(f"     Type: {match['match_type']}, Family: {match['family']}")

    print(f"\n❌ Missing Skills: {', '.join(analysis['missing_skills'])}")