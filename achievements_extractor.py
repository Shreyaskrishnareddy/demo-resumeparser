#!/usr/bin/env python3
"""
Achievements Extractor for Resume Processing
Extracts achievements and accomplishments from various resume sections as per BRD
"""

import re
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class AchievementsExtractor:
    def __init__(self):
        """Initialize the achievements extractor"""
        self.achievement_headers = {
            'achievements', 'accomplishments', 'awards', 'honors', 'recognition',
            'notable achievements', 'key accomplishments', 'major achievements',
            'career highlights', 'highlights', 'distinctions', 'accolades'
        }

        self.achievement_indicators = {
            'awarded', 'recognized', 'achieved', 'exceeded', 'improved', 'increased',
            'reduced', 'saved', 'generated', 'delivered', 'led', 'managed',
            'successful', 'winner', 'champion', 'top', 'best', 'first', 'record'
        }

        self.quantifier_patterns = [
            r'\d+(?:\.\d+)?%',  # Percentages (allow decimals)
            r'\$[\d,]+(?:\.\d+)?[kmb]?',  # Dollar amounts with suffixes
            r'\d+(?:\.\d+)?[kmb]',  # Numbers with k/m/b suffixes
            r'\d+\s*(?:million|thousand|billion)',  # Written numbers
            r'\d+\s*(?:hours?|days?|weeks?|months?|years?)',  # Time periods
            r'\d+\s*(?:people|employees|users|customers|clients)',  # People counts
            r'\d+(?:\.\d+)?x',  # Multipliers (e.g., 2x, 1.5x)
            r'(?:increased|improved|reduced|saved|generated|delivered)\s+(?:by\s+)?\d+',  # Action + number
            r'\d+(?:\.\d+)?\s*(?:times|fold)',  # Times/fold improvements
            r'(?:over|under|within)\s+\d+',  # Time constraints
            r'\d+\+',  # Numbers with plus (indicating "or more")
        ]

        logger.info("🏆 Achievements Extractor initialized")

    def extract_achievements(self, resume_text: str, experience_data: List[Dict] = None) -> List[Dict]:
        """
        Extract achievements from resume text and experience data

        Args:
            resume_text: Full resume text
            experience_data: Parsed experience history

        Returns:
            List of achievement dictionaries
        """
        achievements = []

        # Method 1: Extract from dedicated achievement sections
        dedicated_achievements = self._extract_from_achievement_sections(resume_text)
        achievements.extend(dedicated_achievements)

        # Method 2: Extract from experience descriptions
        if experience_data:
            experience_achievements = self._extract_from_experience(experience_data)
            achievements.extend(experience_achievements)

        # Method 3: Extract from other sections (education, summary, etc.)
        general_achievements = self._extract_from_general_text(resume_text)
        achievements.extend(general_achievements)

        # Remove duplicates and enhance data
        unique_achievements = self._deduplicate_achievements(achievements)
        enhanced_achievements = [self._enhance_achievement_data(ach) for ach in unique_achievements]

        return enhanced_achievements

    def _extract_from_achievement_sections(self, text: str) -> List[Dict]:
        """Extract achievements from dedicated achievement sections"""
        achievements = []
        lines = text.split('\n')

        # Find achievement section boundaries
        achievement_sections = self._find_achievement_sections(lines)

        for section_start, section_end in achievement_sections:
            section_text = '\n'.join(lines[section_start:section_end])
            section_achievements = self._parse_achievement_section(section_text)
            achievements.extend(section_achievements)

        return achievements

    def _find_achievement_sections(self, lines: List[str]) -> List[Tuple[int, int]]:
        """Find the boundaries of achievement sections"""
        sections = []
        current_section = None

        for i, line in enumerate(lines):
            line_clean = line.strip().lower()

            # Check if line is an achievement section header
            if self._is_achievement_header(line_clean):
                if current_section is not None:
                    sections.append((current_section, i))
                current_section = i + 1

            # Check if we've hit another major section
            elif current_section is not None and self._is_major_section_header(line_clean):
                sections.append((current_section, i))
                current_section = None

        # Close last section if needed
        if current_section is not None:
            sections.append((current_section, len(lines)))

        return sections

    def _is_achievement_header(self, line: str) -> bool:
        """Check if line is an achievement section header"""
        clean_line = re.sub(r'[^\w\s]', ' ', line).strip()
        return any(header in clean_line for header in self.achievement_headers)

    def _is_major_section_header(self, line: str) -> bool:
        """Check if line indicates start of a new major section"""
        major_sections = {
            'experience', 'work experience', 'employment', 'employment history',
            'education', 'skills', 'certifications', 'projects', 'references',
            'contact', 'summary', 'objective', 'profile'
        }

        clean_line = re.sub(r'[^\w\s]', ' ', line).strip()
        return any(section in clean_line for section in major_sections)

    def _parse_achievement_section(self, section_text: str) -> List[Dict]:
        """Parse individual achievement entries from an achievement section"""
        achievements = []
        lines = [line.strip() for line in section_text.split('\n') if line.strip()]

        current_achievement = None

        for line in lines:
            # Check if line starts a new achievement
            if self._looks_like_achievement_start(line):
                if current_achievement:
                    achievements.append(current_achievement)

                current_achievement = {
                    'description': line,
                    'category': 'achievement',
                    'source': 'dedicated_section',
                    'quantified': self._is_quantified(line),
                    'quantified_result': self._extract_quantified_result(line),
                    'metrics': self._extract_metrics(line)
                }
            elif current_achievement:
                # Continue current achievement description
                current_achievement['description'] += ' ' + line

        # Add final achievement
        if current_achievement:
            achievements.append(current_achievement)

        return achievements

    def _looks_like_achievement_start(self, line: str) -> bool:
        """Check if line looks like the start of an achievement"""
        # Achievement lines often:
        # - Start with bullet points
        # - Contain achievement indicators
        # - Are not too short

        if len(line) < 10:
            return False

        # Check for bullet points
        if line.startswith(('•', '-', '*', '◦')) or re.match(r'^\d+\.', line):
            return True

        # Check for achievement indicators
        has_indicator = any(indicator in line.lower() for indicator in self.achievement_indicators)

        # Check for quantifiers
        has_quantifier = any(re.search(pattern, line) for pattern in self.quantifier_patterns)

        return has_indicator or has_quantifier

    def _extract_from_experience(self, experience_data: List[Dict]) -> List[Dict]:
        """Extract achievements mentioned in experience descriptions"""
        achievements = []

        for exp in experience_data:
            company = exp.get('company', '')
            role = exp.get('title', '')
            start_date = exp.get('start_date', '')
            end_date = exp.get('end_date', '')
            description = exp.get('description', '')

            # Find achievement statements in description
            exp_achievements = self._find_achievements_in_description(description)

            # Enhance with experience context
            for achievement in exp_achievements:
                achievement['company'] = company
                achievement['role'] = role
                achievement['period'] = f"{start_date} - {end_date}"
                achievement['source'] = 'experience_description'

            achievements.extend(exp_achievements)

        return achievements

    def _find_achievements_in_description(self, description: str) -> List[Dict]:
        """Find achievement statements within job descriptions"""
        achievements = []

        # Split description into sentences/bullet points
        sentences = self._split_into_statements(description)

        for sentence in sentences:
            if self._is_achievement_statement(sentence):
                achievement = {
                    'description': sentence.strip(),
                    'category': self._categorize_achievement(sentence),
                    'quantified': self._is_quantified(sentence),
                    'quantified_result': self._extract_quantified_result(sentence),
                    'metrics': self._extract_metrics(sentence),
                    'impact_level': self._assess_impact_level(sentence)
                }
                achievements.append(achievement)

        return achievements

    def _split_into_statements(self, text: str) -> List[str]:
        """Split text into individual statements/sentences"""
        # Split by bullet points first
        bullet_pattern = r'(?:^|\n)\s*[•\-*◦]\s*'
        statements = re.split(bullet_pattern, text)

        # Further split by sentences if no bullet points
        if len(statements) <= 1:
            statements = re.split(r'[.!?]+\s+', text)

        return [stmt.strip() for stmt in statements if stmt.strip()]

    def _is_achievement_statement(self, statement: str) -> bool:
        """Check if statement describes an achievement"""
        statement_lower = statement.lower()

        # Check for achievement indicators
        has_indicator = any(indicator in statement_lower for indicator in self.achievement_indicators)

        # Check for quantifiable results
        has_quantifier = any(re.search(pattern, statement) for pattern in self.quantifier_patterns)

        # Check for positive impact words
        positive_words = {
            'increased', 'improved', 'enhanced', 'optimized', 'streamlined',
            'reduced', 'decreased', 'minimized', 'eliminated', 'saved',
            'generated', 'created', 'developed', 'launched', 'delivered',
            'exceeded', 'surpassed', 'achieved', 'accomplished', 'successful'
        }

        has_positive_impact = any(word in statement_lower for word in positive_words)

        # Must have at least one indicator and be substantial
        return (has_indicator or has_quantifier or has_positive_impact) and len(statement) > 20

    def _extract_from_general_text(self, text: str) -> List[Dict]:
        """Extract achievements from general resume text (summary, etc.)"""
        achievements = []

        # Look for achievement patterns in summary/objective sections
        summary_pattern = r'(?:summary|objective|profile)(?:\s*[:])?\s*([^.]+(?:\.|$))'
        matches = re.finditer(summary_pattern, text, re.IGNORECASE | re.MULTILINE)

        for match in matches:
            summary_text = match.group(1)
            if self._is_achievement_statement(summary_text):
                achievement = {
                    'description': summary_text.strip(),
                    'category': 'summary_achievement',
                    'source': 'summary_section',
                    'quantified': self._is_quantified(summary_text),
                    'quantified_result': self._extract_quantified_result(summary_text),
                    'metrics': self._extract_metrics(summary_text)
                }
                achievements.append(achievement)

        # Enhanced: Parse plain achievement statements that don't follow section patterns
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 20 and self._is_achievement_statement(line):
                achievement = {
                    'description': line,
                    'category': self._categorize_achievement(line),
                    'source': 'general_text',
                    'quantified': self._is_quantified(line),
                    'quantified_result': self._extract_quantified_result(line),
                    'metrics': self._extract_metrics(line),
                    'impact_category': self._assess_impact_level(line)
                }
                achievements.append(achievement)

        return achievements

    def _is_quantified(self, text: str) -> bool:
        """Check if achievement is quantified with numbers/metrics"""
        return any(re.search(pattern, text) for pattern in self.quantifier_patterns)

    def _extract_quantified_result(self, text: str) -> str:
        """Extract the specific quantified result from achievement text"""
        if not self._is_quantified(text):
            return ""

        # Extract all quantifiers and return the most significant one
        quantifiers = []

        for pattern in self.quantifier_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                quantifiers.append(match.group(0))

        # Return the first quantifier found, or combine if multiple
        if quantifiers:
            return ', '.join(quantifiers[:2])  # Limit to first 2 most important

        return ""

    def _extract_metrics(self, text: str) -> List[Dict]:
        """Extract specific metrics from achievement text"""
        metrics = []

        # Extract percentages
        percentage_matches = re.finditer(r'(\d+(?:\.\d+)?)\s*%', text)
        for match in percentage_matches:
            metrics.append({
                'type': 'percentage',
                'value': float(match.group(1)),
                'unit': '%',
                'context': self._extract_context(text, match.span())
            })

        # Extract dollar amounts
        dollar_matches = re.finditer(r'\$\s*([\d,]+(?:\.\d+)?)\s*([kmb]?)', text, re.IGNORECASE)
        for match in dollar_matches:
            value = float(match.group(1).replace(',', ''))
            multiplier = {'k': 1000, 'm': 1000000, 'b': 1000000000}.get(match.group(2).lower(), 1)
            metrics.append({
                'type': 'currency',
                'value': value * multiplier,
                'unit': 'USD',
                'context': self._extract_context(text, match.span())
            })

        # Extract time periods
        time_matches = re.finditer(r'(\d+)\s*(hours?|days?|weeks?|months?|years?)', text, re.IGNORECASE)
        for match in time_matches:
            metrics.append({
                'type': 'time',
                'value': int(match.group(1)),
                'unit': match.group(2).lower(),
                'context': self._extract_context(text, match.span())
            })

        return metrics

    def _extract_context(self, text: str, span: Tuple[int, int]) -> str:
        """Extract context around a metric"""
        start, end = span
        context_start = max(0, start - 20)
        context_end = min(len(text), end + 20)
        return text[context_start:context_end].strip()

    def _categorize_achievement(self, text: str) -> str:
        """Categorize achievement by type"""
        text_lower = text.lower()

        categories = {
            'financial': ['revenue', 'profit', 'cost', 'budget', 'savings', 'sales', '$'],
            'performance': ['efficiency', 'productivity', 'performance', 'speed', 'time'],
            'quality': ['quality', 'accuracy', 'error', 'defect', 'satisfaction'],
            'growth': ['growth', 'expansion', 'scale', 'increase', 'users', 'customers'],
            'leadership': ['led', 'managed', 'directed', 'supervised', 'team'],
            'innovation': ['created', 'developed', 'designed', 'innovated', 'built'],
            'recognition': ['award', 'recognition', 'honored', 'winner', 'top']
        }

        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category

        return 'general'

    def _assess_impact_level(self, text: str) -> str:
        """Assess the impact level of an achievement"""
        # High impact indicators
        high_impact = ['million', 'billion', 'company-wide', 'organization', 'enterprise']

        # Medium impact indicators
        medium_impact = ['department', 'team', 'division', 'significant', 'major']

        # Low impact indicators
        low_impact = ['personal', 'individual', 'small', 'minor']

        text_lower = text.lower()

        if any(indicator in text_lower for indicator in high_impact):
            return 'high'
        elif any(indicator in text_lower for indicator in medium_impact):
            return 'medium'
        elif any(indicator in text_lower for indicator in low_impact):
            return 'low'
        else:
            # Assess based on quantifiers
            if self._is_quantified(text):
                return 'medium'
            else:
                return 'low'

    def _deduplicate_achievements(self, achievements: List[Dict]) -> List[Dict]:
        """Remove duplicate achievements"""
        unique_achievements = []
        seen_descriptions = set()

        for achievement in achievements:
            description = achievement.get('description', '').lower().strip()

            # Simple deduplication based on description similarity
            is_duplicate = False
            for seen in seen_descriptions:
                if self._calculate_similarity(description, seen) > 0.8:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_achievements.append(achievement)
                seen_descriptions.add(description)

        return unique_achievements

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        if not text1 or not text2:
            return 0.0

        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _enhance_achievement_data(self, achievement: Dict) -> Dict:
        """Enhance achievement data with additional analysis"""
        # Calculate achievement score based on various factors
        score = self._calculate_achievement_score(achievement)
        achievement['achievement_score'] = score

        # Add keyword tags
        achievement['tags'] = self._extract_achievement_tags(achievement.get('description', ''))

        return achievement

    def _calculate_achievement_score(self, achievement: Dict) -> int:
        """Calculate achievement importance score (1-10)"""
        score = 1

        # Base score from quantification
        if achievement.get('quantified', False):
            score += 3

        # Add points for impact level
        impact_level = achievement.get('impact_level', 'low')
        impact_scores = {'high': 4, 'medium': 2, 'low': 1}
        score += impact_scores.get(impact_level, 1)

        # Add points for category
        category = achievement.get('category', 'general')
        high_value_categories = {'financial', 'leadership', 'innovation'}
        if category in high_value_categories:
            score += 2

        # Add points for metrics
        metrics_count = len(achievement.get('metrics', []))
        score += min(2, metrics_count)

        return min(10, score)

    def _extract_achievement_tags(self, description: str) -> List[str]:
        """Extract relevant tags from achievement description"""
        tags = []
        description_lower = description.lower()

        tag_keywords = {
            'leadership': ['led', 'managed', 'directed', 'supervised'],
            'teamwork': ['team', 'collaboration', 'coordinated'],
            'innovation': ['created', 'developed', 'designed', 'built'],
            'efficiency': ['improved', 'optimized', 'streamlined'],
            'growth': ['increased', 'grew', 'expanded', 'scaled'],
            'cost_savings': ['reduced', 'saved', 'cut', 'minimized'],
            'quality': ['quality', 'accuracy', 'excellence'],
            'customer_focus': ['customer', 'client', 'satisfaction']
        }

        for tag, keywords in tag_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                tags.append(tag)

        return tags

# Example usage and testing
if __name__ == "__main__":
    extractor = AchievementsExtractor()

    # Test with sample resume text
    sample_text = """
    ACHIEVEMENTS
    • Increased sales revenue by 35% in first quarter, generating $2.5M additional income
    • Led a team of 8 developers to deliver project 2 weeks ahead of schedule
    • Reduced operational costs by $500K annually through process optimization
    • Awarded "Employee of the Year" for outstanding performance

    EXPERIENCE
    Senior Manager at TechCorp (2021-2023)
    - Successfully managed a $10M budget for digital transformation
    - Improved customer satisfaction scores from 7.2 to 9.1 (32% increase)
    - Launched 3 new products that captured 15% market share
    """

    print("🏆 Achievements Extraction Test:")
    print("=" * 50)

    achievements = extractor.extract_achievements(sample_text)

    for i, achievement in enumerate(achievements, 1):
        print(f"\n🎯 Achievement {i}:")
        print(f"   Description: {achievement.get('description', 'N/A')[:100]}...")
        print(f"   Category: {achievement.get('category', 'N/A')}")
        print(f"   Quantified: {achievement.get('quantified', False)}")
        print(f"   Impact Level: {achievement.get('impact_level', 'N/A')}")
        print(f"   Score: {achievement.get('achievement_score', 'N/A')}/10")
        print(f"   Tags: {', '.join(achievement.get('tags', []))}")
        print(f"   Source: {achievement.get('source', 'N/A')}")

        if achievement.get('metrics'):
            print(f"   Metrics: {len(achievement['metrics'])} found")

    def get_quantified_achievements(self, achievements: List[Dict]) -> List[Dict]:
        """
        Get achievements that have quantified metrics
        Required by BRD compliance testing

        Args:
            achievements: List of achievement dictionaries

        Returns:
            List of achievements with quantified metrics
        """
        quantified = []
        for achievement in achievements:
            if achievement.get('quantified', False) or achievement.get('metrics', []):
                quantified.append(achievement)
        return quantified

    def categorize_achievements_by_impact(self, achievements: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize achievements by impact areas
        Required by BRD compliance testing

        Args:
            achievements: List of achievement dictionaries

        Returns:
            Dictionary mapping impact categories to achievement lists
        """
        categorized = {
            'financial': [],
            'operational': [],
            'leadership': [],
            'innovation': [],
            'customer': [],
            'quality': [],
            'other': []
        }

        for achievement in achievements:
            category = self._assess_impact_level(achievement.get('description', ''))
            categorized[category].append(achievement)

        return categorized

    def _determine_impact_category(self, achievement: Dict) -> str:
        """Determine the impact category for an achievement"""
        description = achievement.get('description', '').lower()

        # Financial impact indicators
        if any(word in description for word in ['revenue', 'profit', 'cost', 'sales', 'budget', '$', 'roi', 'savings']):
            return 'financial'

        # Operational impact indicators
        elif any(word in description for word in ['efficiency', 'process', 'time', 'reduced', 'optimized', 'automated']):
            return 'operational'

        # Leadership impact indicators
        elif any(word in description for word in ['led', 'managed', 'team', 'people', 'mentor', 'trained']):
            return 'leadership'

        # Innovation impact indicators
        elif any(word in description for word in ['new', 'innovative', 'created', 'developed', 'designed', 'patent']):
            return 'innovation'

        # Customer impact indicators
        elif any(word in description for word in ['customer', 'client', 'user', 'satisfaction', 'experience', 'service']):
            return 'customer'

        # Quality impact indicators
        elif any(word in description for word in ['quality', 'accuracy', 'reliability', 'testing', 'bugs', 'defects']):
            return 'quality'

        else:
            return 'other'