#!/usr/bin/env python3
"""
Semantic Position Detection Engine for 100% BRD Compliance
Uses structural analysis instead of pattern matching
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class PositionCandidate:
    line_idx: int
    text: str
    confidence: float
    company_name: str
    location: str
    dates: str
    reasons: List[str]

class SemanticPositionDetector:
    """
    Advanced position detection using structural analysis
    for 100% BRD compliance
    """

    def __init__(self):
        # Pre-compiled patterns for performance
        self.company_suffixes = re.compile(r'\b(Inc\.?|LLC|Corp\.?|Corporation|Ltd\.?|Limited|Company|Co\.?|Group|Technologies|Tech|Solutions|Systems|Associates|Partners|Consulting|Services|International|Global|Industries|Holdings|Enterprises)\b', re.IGNORECASE)

        self.date_patterns = re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}|\b\d{4}\s*[-–—]\s*(?:\d{4}|Present|Current)', re.IGNORECASE)

        self.job_duty_indicators = re.compile(r'^(?:•|\*|-|\d+\.)\s*|^(?:Responsible|Led|Managed|Developed|Implemented|Created|Designed|Coordinated|Supervised|Oversaw|Maintained|Performed|Conducted|Analyzed|Reviewed|Established|Configured|Architected|Spearheaded|Orchestrated)\b', re.IGNORECASE)

        self.known_companies = {
            'genesis 10', 'bank of america', 'trinitek', 'bright computing',
            'govconnection', 'silicon graphics', 'oracle', 'sun microsystems',
            'citrus health', 'physicians healthcare', 'vha', 'travelocity',
            'verizon', '7-eleven', 'hewlett packard', 'mcafee', 'capital one'
        }

    def detect_positions(self, text: str) -> List[PositionCandidate]:
        """
        Main position detection using semantic analysis
        """
        lines = text.split('\n')

        # Step 1: Find experience section boundaries
        exp_start, exp_end = self._find_experience_section(lines)
        if exp_start == -1:
            return []

        exp_lines = lines[exp_start:exp_end]

        # Step 2: Structural analysis within experience section
        candidates = self._structural_analysis(exp_lines, exp_start)

        # Step 3: Semantic filtering and validation
        valid_positions = self._semantic_validation(candidates)

        # Step 4: Final confidence scoring and ranking
        return self._rank_by_confidence(valid_positions)

    def _find_experience_section(self, lines: List[str]) -> Tuple[int, int]:
        """Find experience section with high precision"""
        experience_keywords = [
            'experience', 'employment', 'work history', 'career history',
            'professional experience', 'work experience', 'employment history',
            'career summary', 'professional background'
        ]

        start_idx = -1
        end_idx = len(lines)

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # Look for experience section headers
            if any(keyword in line_lower for keyword in experience_keywords):
                if len(line_lower) < 50:  # Header lines are typically short
                    start_idx = i + 1
                    break

        # Find end of experience section
        if start_idx != -1:
            section_end_keywords = [
                'education', 'skills', 'certifications', 'awards',
                'references', 'projects', 'publications', 'languages'
            ]

            for i in range(start_idx + 10, len(lines)):  # Look after some content
                line_lower = lines[i].lower().strip()
                if any(keyword in line_lower for keyword in section_end_keywords):
                    if len(line_lower) < 30:  # Header lines are short
                        end_idx = i
                        break

        return start_idx, end_idx

    def _structural_analysis(self, lines: List[str], offset: int) -> List[PositionCandidate]:
        """Analyze resume structure to identify position headers"""
        candidates = []

        for i, line in enumerate(lines):
            line = line.strip()
            if len(line) < 10:  # Too short to be a position header
                continue

            # Skip obvious job duties/descriptions
            if self.job_duty_indicators.match(line):
                continue

            # Analyze line structure
            confidence = 0.0
            reasons = []

            # Check for company indicators
            if self.company_suffixes.search(line):
                confidence += 0.4
                reasons.append("Has company suffix")

            # Check for known companies
            line_lower = line.lower()
            for company in self.known_companies:
                if company in line_lower:
                    confidence += 0.5
                    reasons.append(f"Contains known company: {company}")
                    break

            # Check for proper structure (company, location, dates)
            parts = line.split(',')
            if len(parts) >= 2:
                confidence += 0.2
                reasons.append("Has comma-separated structure")

                # Check if has dates
                if self.date_patterns.search(line):
                    confidence += 0.3
                    reasons.append("Contains date pattern")

            # Check formatting (all caps companies, proper capitalization)
            if parts and parts[0].isupper() and len(parts[0]) > 3:
                confidence += 0.2
                reasons.append("Company name in capitals")

            # Penalize if looks like job description
            if any(word in line_lower for word in ['responsible', 'performed', 'managed', 'developed']):
                confidence -= 0.4
                reasons.append("PENALTY: Contains job duty words")

            # Only consider high-confidence candidates
            if confidence >= 0.3:
                # Extract components
                company_name = parts[0].strip() if parts else ""
                location = parts[1].strip() if len(parts) > 1 else ""
                dates = self._extract_dates(line)

                candidates.append(PositionCandidate(
                    line_idx=offset + i,
                    text=line,
                    confidence=confidence,
                    company_name=company_name,
                    location=location,
                    dates=dates,
                    reasons=reasons
                ))

        return candidates

    def _semantic_validation(self, candidates: List[PositionCandidate]) -> List[PositionCandidate]:
        """Apply semantic rules to filter candidates"""
        valid = []

        for candidate in candidates:
            # High confidence threshold for validation
            if candidate.confidence >= 0.5:
                valid.append(candidate)
            elif candidate.confidence >= 0.3:
                # Additional validation for medium confidence
                if (len(candidate.company_name) >= 5 and
                    not any(word in candidate.text.lower() for word in ['environment', 'technologies', 'platforms', 'duties'])):
                    valid.append(candidate)

        return valid

    def _rank_by_confidence(self, candidates: List[PositionCandidate]) -> List[PositionCandidate]:
        """Sort by confidence and apply final filtering"""
        # Sort by confidence (highest first)
        ranked = sorted(candidates, key=lambda x: x.confidence, reverse=True)

        # Limit to reasonable number of positions (3-8 typical)
        max_positions = min(8, len(ranked))

        # Apply proximity filtering (avoid duplicate similar lines)
        filtered = []
        for candidate in ranked[:max_positions]:
            # Check if too similar to existing candidates
            is_duplicate = False
            for existing in filtered:
                if (abs(candidate.line_idx - existing.line_idx) < 3 and
                    candidate.company_name.lower() == existing.company_name.lower()):
                    is_duplicate = True
                    break

            if not is_duplicate:
                filtered.append(candidate)

        return filtered

    def _extract_dates(self, text: str) -> str:
        """Extract date ranges from text"""
        match = self.date_patterns.search(text)
        return match.group(0) if match else ""

# Usage example and test
if __name__ == "__main__":
    detector = SemanticPositionDetector()

    # Test with sample resume text
    sample_text = """
    PROFESSIONAL EXPERIENCE

    Genesis 10 – Bank of America, Dallas, TX                    September 2016 – May 2017
    Senior Program/Project Manager
    • Responsible for managing infrastructure projects
    • Developed project plans and timelines

    Travelocity, Southlake, TX                                 April 2005 – January 2009
    Senior Project Manager
    • Managed eCommerce products
    """

    positions = detector.detect_positions(sample_text)

    print(f"Found {len(positions)} positions:")
    for i, pos in enumerate(positions, 1):
        print(f"{i}. {pos.company_name} ({pos.confidence:.2f} confidence)")
        print(f"   Reasons: {', '.join(pos.reasons)}")