#!/usr/bin/env python3
"""
Name Parser for Resume Processing
Splits full names into First, Middle, Last components as per BRD requirements
"""

import re
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class NameParser:
    def __init__(self):
        """Initialize the name parser"""
        self.prefixes = {
            'mr', 'mrs', 'ms', 'miss', 'dr', 'doctor', 'prof', 'professor',
            'rev', 'reverend', 'hon', 'honorable', 'sir', 'madam', 'lady',
            'lord', 'count', 'countess', 'duke', 'duchess', 'baron', 'baroness'
        }

        self.suffixes = {
            'jr', 'junior', 'sr', 'senior', 'ii', 'iii', 'iv', 'v',
            'phd', 'md', 'dds', 'jd', 'esq', 'esquire', 'cpa', 'rn',
            'pe', 'pmp', 'mba', 'ms', 'ma', 'bs', 'ba', 'bsc', 'beng',
            'dvm', 'dpt', 'ot', 'pt', 'np', 'pa', 'cfa', 'cma', 'cissp'
        }

        self.conjunctions = {'and', 'y', 'e', 'et', 'und', 'og'}

        # Common particles in names from various cultures
        self.particles = {
            'de', 'del', 'della', 'di', 'da', 'das', 'dos', 'du', 'van', 'von',
            'der', 'den', 'ter', 'ten', 'op', 'aan', 'bin', 'ibn', 'abu',
            'al', 'el', 'la', 'le', 'les', 'lo', 'mac', 'mc', "o'", 'ben',
            'bat', 'ibn', 'bint', 'abd', 'abdul'
        }

        logger.info("👤 Name Parser initialized with cultural patterns")

    def parse_name(self, full_name: str) -> Dict[str, str]:
        """
        Parse a full name into components

        Args:
            full_name: The complete name string from resume

        Returns:
            Dictionary with First Name, Middle Name, Last Name components
        """
        if not full_name or not full_name.strip():
            return {
                'Full Name': '',
                'First Name': '',
                'Middle Name': '',
                'Last Name': ''
            }

        # Clean and normalize the name
        cleaned_name = self._clean_name(full_name)

        # Split into tokens
        tokens = self._tokenize_name(cleaned_name)

        if not tokens:
            return {
                'Full Name': full_name.strip(),
                'First Name': '',
                'Middle Name': '',
                'Last Name': ''
            }

        # Remove prefixes and suffixes
        core_tokens, prefixes, suffixes = self._extract_prefixes_suffixes(tokens)

        # Parse the core name components
        first, middle, last = self._parse_core_name(core_tokens)

        # Format the results
        result = {
            'Full Name': full_name.strip(),
            'First Name': first,
            'Middle Name': middle,
            'Last Name': last
        }

        # Add prefix/suffix info if needed for debugging
        if prefixes or suffixes:
            result['_prefixes'] = ' '.join(prefixes) if prefixes else ''
            result['_suffixes'] = ' '.join(suffixes) if suffixes else ''

        return result

    def _clean_name(self, name: str) -> str:
        """Clean and normalize the name string"""
        # Remove extra whitespace and normalize
        name = ' '.join(name.split())

        # Remove common resume artifacts
        name = re.sub(r'\b(resume|cv|curriculum vitae)\b', '', name, flags=re.IGNORECASE)

        # Remove email patterns that might be mixed in
        name = re.sub(r'\S+@\S+\.\S+', '', name)

        # Remove phone number patterns
        name = re.sub(r'[\(\[]?\d{3}[\)\]]?[-.\s]?\d{3}[-.\s]?\d{4}', '', name)

        # Remove excessive punctuation but keep apostrophes, hyphens, periods in names
        name = re.sub(r'[^\w\s\'-.]', ' ', name)

        # Clean up multiple spaces
        name = ' '.join(name.split())

        return name.strip()

    def _tokenize_name(self, name: str) -> List[str]:
        """Split name into tokens while preserving compound parts"""
        # Handle hyphenated names and apostrophes
        tokens = []

        # Split by spaces but keep hyphenated parts together
        parts = name.split()

        for part in parts:
            # Skip empty parts
            if not part:
                continue

            # Skip parts that are clearly not names (numbers, single letters unless common)
            if re.match(r'^\d+$', part) or (len(part) == 1 and part.lower() not in 'aio'):
                continue

            tokens.append(part)

        return tokens

    def _extract_prefixes_suffixes(self, tokens: List[str]) -> Tuple[List[str], List[str], List[str]]:
        """Extract prefixes and suffixes from name tokens"""
        if not tokens:
            return [], [], []

        prefixes = []
        suffixes = []
        core_tokens = tokens.copy()

        # Extract prefixes from the beginning
        while core_tokens and self._is_prefix(core_tokens[0]):
            prefixes.append(core_tokens.pop(0))

        # Extract suffixes from the end
        while core_tokens and self._is_suffix(core_tokens[-1]):
            suffixes.insert(0, core_tokens.pop())

        return core_tokens, prefixes, suffixes

    def _is_prefix(self, token: str) -> bool:
        """Check if token is a name prefix"""
        clean_token = re.sub(r'[^\w]', '', token.lower())
        return clean_token in self.prefixes

    def _is_suffix(self, token: str) -> bool:
        """Check if token is a name suffix"""
        clean_token = re.sub(r'[^\w]', '', token.lower())
        return clean_token in self.suffixes

    def _parse_core_name(self, tokens: List[str]) -> Tuple[str, str, str]:
        """Parse core name tokens into first, middle, last"""
        if not tokens:
            return '', '', ''

        if len(tokens) == 1:
            # Single name - assume it's first name
            return tokens[0], '', ''

        elif len(tokens) == 2:
            # Two names - first and last
            return tokens[0], '', tokens[1]

        elif len(tokens) == 3:
            # Three names - first, middle, last
            return tokens[0], tokens[1], tokens[2]

        else:
            # More than three names - need to determine structure
            return self._parse_complex_name(tokens)

    def _parse_complex_name(self, tokens: List[str]) -> Tuple[str, str, str]:
        """Parse complex names with multiple components"""
        if len(tokens) < 2:
            return tokens[0] if tokens else '', '', ''

        # Special handling for known cultural patterns
        if len(tokens) == 4:
            # Handle patterns like "Maria de la Cruz" -> "Maria" | "" | "de la Cruz"
            if self._is_particle(tokens[1]) and self._is_particle(tokens[2]):
                return tokens[0], '', ' '.join(tokens[1:])
            # Handle patterns like "Ahmed bin Mohammed Al-Rashid" -> "Ahmed" | "bin Mohammed" | "Al-Rashid"
            elif self._is_particle(tokens[1]) and not self._is_particle(tokens[2]):
                return tokens[0], ' '.join(tokens[1:3]), tokens[3]

        # Check for particles that should stay with last name
        last_name_start = self._find_last_name_start(tokens)

        if last_name_start == 0:
            # All tokens are part of last name (unusual but possible)
            return '', '', ' '.join(tokens)

        elif last_name_start == 1:
            # First token is first name, rest is last name
            return tokens[0], '', ' '.join(tokens[1:])

        else:
            # Normal case: first name, middle names, last name
            first_name = tokens[0]
            last_name = ' '.join(tokens[last_name_start:])
            middle_name = ' '.join(tokens[1:last_name_start])

            return first_name, middle_name, last_name

    def _find_last_name_start(self, tokens: List[str]) -> int:
        """Find where the last name starts in the token list"""
        # Look for particles that indicate last name components
        for i in range(len(tokens) - 1, 0, -1):
            if tokens[i - 1].lower() in self.particles:
                return i - 1

        # Check for capitalization patterns (all caps might be last name)
        for i in range(len(tokens) - 1, 0, -1):
            if tokens[i].isupper() and len(tokens[i]) > 1:
                return i

        # Default: assume last token or last two tokens are surname
        if len(tokens) > 3:
            return len(tokens) - 1
        else:
            return len(tokens) - 1

    def _is_particle(self, token: str) -> bool:
        """Check if token is a name particle"""
        return token.lower() in self.particles

    def validate_parsed_name(self, parsed_name: Dict[str, str]) -> Dict[str, any]:
        """Validate the parsed name components"""
        validation = {
            'is_valid': True,
            'confidence': 1.0,
            'issues': []
        }

        first_name = parsed_name.get('First Name', '')
        middle_name = parsed_name.get('Middle Name', '')
        last_name = parsed_name.get('Last Name', '')

        # Check if we have at least a first or last name
        if not first_name and not last_name:
            validation['is_valid'] = False
            validation['confidence'] = 0.0
            validation['issues'].append('No recognizable first or last name found')
            return validation

        # Check for reasonable name lengths
        if first_name and len(first_name) > 50:
            validation['confidence'] *= 0.7
            validation['issues'].append('First name unusually long')

        if last_name and len(last_name) > 50:
            validation['confidence'] *= 0.7
            validation['issues'].append('Last name unusually long')

        if middle_name and len(middle_name) > 100:
            validation['confidence'] *= 0.8
            validation['issues'].append('Middle name unusually long')

        # Check for numeric characters in names (usually indicates parsing errors)
        for component, value in [('First', first_name), ('Middle', middle_name), ('Last', last_name)]:
            if value and re.search(r'\d', value):
                validation['confidence'] *= 0.5
                validation['issues'].append(f'{component} name contains numbers')

        return validation

    def extract_name_from_resume_text(self, text: str) -> Dict[str, str]:
        """Extract name from resume text using common patterns"""
        lines = text.split('\n')

        # Try different strategies to find the name
        candidates = []

        # Strategy 1: Look for name in first few lines
        for i, line in enumerate(lines[:5]):
            line = line.strip()
            if self._looks_like_name_line(line):
                candidates.append((line, i, 'header_line'))

        # Strategy 2: Look for "Name:" or similar patterns
        name_patterns = [
            r'(?:name|full name|candidate name):\s*(.+)',
            r'(?:applicant|candidate):\s*(.+)',
            r'^([A-Z][a-z]+ [A-Z][a-z]+.*?)(?:\s|$)',  # Capitalized words pattern
        ]

        for pattern in name_patterns:
            for line in lines[:10]:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    candidates.append((match.group(1).strip(), 0, 'pattern_match'))

        # Strategy 3: Look for isolated name-like text in early lines
        for i, line in enumerate(lines[:3]):
            words = line.split()
            if 2 <= len(words) <= 5 and all(self._looks_like_name_word(word) for word in words):
                candidates.append((line.strip(), i, 'isolated_name'))

        # Choose the best candidate
        if candidates:
            # Prefer earlier lines and certain patterns
            best_candidate = min(candidates, key=lambda x: (x[1], 0 if x[2] == 'pattern_match' else 1))
            return self.parse_name(best_candidate[0])

        # Fallback: try to extract from the very first line
        first_line = lines[0].strip() if lines else ''
        return self.parse_name(first_line)

    def _looks_like_name_line(self, line: str) -> bool:
        """Check if a line looks like it contains a name"""
        if not line or len(line) > 100:
            return False

        # Remove common non-name patterns
        if re.search(r'@|\.com|phone|email|address|resume|cv', line, re.IGNORECASE):
            return False

        # Check if it has name-like words
        words = line.split()
        if not (2 <= len(words) <= 6):
            return False

        return all(self._looks_like_name_word(word) for word in words)

    def _looks_like_name_word(self, word: str) -> bool:
        """Check if a word looks like part of a name"""
        # Remove punctuation for checking
        clean_word = re.sub(r'[^\w\'-]', '', word)

        if not clean_word or len(clean_word) < 2:
            return False

        # Should start with capital letter
        if not clean_word[0].isupper():
            return False

        # Should not be all uppercase (unless short)
        if clean_word.isupper() and len(clean_word) > 3:
            return False

        # Should not contain numbers
        if re.search(r'\d', clean_word):
            return False

        return True

# Example usage and testing
if __name__ == "__main__":
    parser = NameParser()

    # Test cases for name parsing
    test_names = [
        "John Smith",
        "Mary Jane Watson",
        "Dr. Robert James Wilson Jr.",
        "Maria de la Cruz",
        "Jean-Paul van der Berg",
        "Ms. Elizabeth Anne Johnson-Brown PhD",
        "Ahmed bin Mohammed Al-Rashid",
        "O'Connor, Patrick Michael",
        "李小明",  # Chinese name
        "José María García López"
    ]

    print("👤 Name Parsing Test Results:")
    print("=" * 60)

    for name in test_names:
        result = parser.parse_name(name)
        validation = parser.validate_parsed_name(result)

        print(f"\n📝 Input: '{name}'")
        print(f"   First: '{result['First Name']}'")
        print(f"   Middle: '{result['Middle Name']}'")
        print(f"   Last: '{result['Last Name']}'")
        print(f"   Confidence: {validation['confidence']:.2f}")
        if validation['issues']:
            print(f"   Issues: {', '.join(validation['issues'])}")

    # Test resume text extraction
    sample_resume = """JOHN MICHAEL SMITH
Software Engineer
Email: john.smith@email.com
Phone: (555) 123-4567

EXPERIENCE
Senior Developer at Tech Corp...
"""

    print(f"\n🔍 Resume Text Extraction:")
    print("=" * 40)
    extracted = parser.extract_name_from_resume_text(sample_resume)
    print(f"Extracted: {extracted}")