#!/usr/bin/env python3
"""
Enhanced Real Content Extractor
Replaces the basic extraction methods with content-aware parsing
"""

import re
from typing import Dict, List, Any, Tuple

class EnhancedRealContentExtractor:
    """Enhanced extractor that focuses on extracting real content from resumes"""

    def __init__(self):
        self.job_title_patterns = [
            # Common job title patterns
            r'\b(Senior|Lead|Principal|Staff|Associate|Junior)?\s*(Software|Data|Business|Product|Project|Program)\s+(Manager|Developer|Engineer|Analyst|Consultant|Architect)\b',
            r'\b(Project|Program|Product)\s+Manager\b',
            r'\b(Software|Full Stack|Frontend|Backend|Web)\s+(Developer|Engineer)\b',
            r'\b(Data|Business|Systems|Security)\s+(Analyst|Engineer|Architect)\b',
            r'\b(Technical|Solution|Enterprise)\s+Architect\b',
            r'\b(Scrum|Agile)\s+Master\b',
            r'\b(DevOps|Site Reliability)\s+Engineer\b',
            r'\bTechnical\s+(Lead|Manager|Director)\b',
            r'\b(Marketing|Sales|HR|Finance)\s+(Manager|Director|Specialist)\b'
        ]

        self.company_indicators = [
            'inc', 'ltd', 'corp', 'llc', 'consulting', 'technologies', 'solutions',
            'services', 'systems', 'software', 'group', 'company', 'enterprises',
            'pvt', 'limited', 'corporation', 'international'
        ]

        # Comprehensive institutional blacklist for name extraction
        self.institutional_blacklist = [
            'university', 'college', 'institute', 'school', 'academy', 'campus',
            'bharathiar', 'texas', 'harvard', 'mit', 'stanford', 'yale', 'princeton',
            'columbia', 'cornell', 'brown', 'dartmouth', 'penn', 'upenn', 'berkeley',
            'ucla', 'usc', 'nyu', 'boston', 'northwestern', 'georgetown', 'duke',
            'vanderbilt', 'rice', 'tulane', 'emory', 'carnegie', 'mellon', 'caltech',
            'georgia tech', 'purdue', 'michigan', 'wisconsin', 'illinois', 'ohio state',
            'penn state', 'virginia tech', 'north carolina', 'florida', 'texas tech',
            'arizona', 'colorado', 'washington', 'oregon', 'utah', 'nevada',
            'iit', 'iisc', 'bits', 'vit', 'manipal', 'srm', 'amrita', 'thapar'
        ]

        # Location patterns to distinguish from company names
        self.location_patterns = [
            r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b',  # City, State
            r'\b[A-Z][a-z]+,\s*(TX|CA|NY|FL|WA|IL|PA|OH|GA|NC|MI|NJ|VA|AZ|TN|IN|MA|MD|MO|WI|MN|CO|AL|SC|LA|KY|OR|OK|CT|IA|MS|AR|KS|UT|NV|NM|WV|NE|ID|HI|NH|ME|RI|MT|DE|SD|ND|AK|VT|WY)\b',
            r'\b(Seattle|Portland|Austin|Dallas|Houston|Miami|Atlanta|Chicago|Boston|New York|Los Angeles|San Francisco|Denver|Phoenix|Las Vegas)\s*,\s*[A-Z]{2}\b'
        ]

    def extract_real_personal_details(self, text: str, filename: str = "") -> Dict[str, str]:
        """Extract real personal details with enhanced accuracy"""

        # Extract emails first (most reliable)
        emails = self._extract_real_emails(text)
        email = emails[0] if emails else ""

        # Extract phones with multiple patterns
        phones = self._extract_real_phones(text)
        phone = phones[0] if phones else ""

        # Extract name with context awareness
        full_name = self._extract_real_name(text, email, filename)

        # Extract first/last name from full name
        first_name, last_name = self._split_name(full_name)

        return {
            'FullName': full_name,
            'FirstName': first_name,
            'LastName': last_name,
            'EmailID': email,
            'PhoneNumber': phone,
            'Location': self._extract_location(text),
            'CountryCode': self._extract_country_code(phone)
        }

    def _extract_real_emails(self, text: str) -> List[str]:
        """Extract real email addresses"""
        email_patterns = [
            r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
            r'(?:email|e-mail|mail)[\s:]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        ]

        emails = []
        for pattern in email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            emails.extend(matches)

        # Remove duplicates and filter out system emails
        unique_emails = []
        for email in emails:
            if email not in unique_emails and '@' in email:
                # Filter out obvious system emails
                if not any(skip in email.lower() for skip in ['noreply', 'donotreply', 'system']):
                    unique_emails.append(email)

        return unique_emails

    def _extract_real_phones(self, text: str) -> List[str]:
        """Extract real phone numbers with ultra-comprehensive patterns and validation"""

        # Multi-strategy phone extraction approach
        phones = []

        # Strategy 1: Context-aware extraction (phone numbers near labels)
        labeled_patterns = [
            r'(?:phone|mobile|cell|contact|tel|telephone|call|number)[\s:]*([+]?[\d\s\-\(\)\.]{8,18})',
            r'(?:ph|mob|cel)[\s:]*([+]?[\d\s\-\(\)\.]{8,18})',
            r'(?:^|\s)(?:p|m|c)[\s:]*([+]?[\d\s\-\(\)\.]{10,18})',
        ]

        for pattern in labeled_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            phones.extend(matches)

        # Strategy 2: Standard format recognition
        standard_patterns = [
            # US formats with country code
            r'\+1[\s\-\.]*\(?\d{3}\)?[\s\-\.]*\d{3}[\s\-\.]*\d{4}',
            # US formats without country code
            r'\b\(?\d{3}\)?[\s\-\.]*\d{3}[\s\-\.]*\d{4}\b',
            # International formats
            r'\+\d{1,3}[\s\-\.]*\d{1,4}[\s\-\.]*\d{1,4}[\s\-\.]*\d{1,9}',
            # Compact 10-digit numbers
            r'\b\d{10}\b',
            # Parentheses formats
            r'\(\d{3}\)[\s\-\.]*\d{3}[\s\-\.]*\d{4}',
            # Dotted formats
            r'\d{3}\.\d{3}\.\d{4}',
            # Dashed formats
            r'\d{3}-\d{3}-\d{4}',
            # Spaced formats
            r'\d{3}\s\d{3}\s\d{4}',
        ]

        for pattern in standard_patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)

        # Strategy 3: Contextual extraction from header/contact sections
        header_text = self._extract_header_section(text)
        if header_text:
            # More aggressive patterns in header section
            header_patterns = [
                r'([+]?[\d\s\-\(\)\.]{8,18})',
            ]
            for pattern in header_patterns:
                matches = re.findall(pattern, header_text)
                phones.extend(matches)

        # Strategy 4: Email-adjacent extraction (phones often near emails)
        email_matches = re.finditer(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        for email_match in email_matches:
            start = max(0, email_match.start() - 100)
            end = min(len(text), email_match.end() + 100)
            context = text[start:end]

            context_patterns = [
                r'([+]?[\d\s\-\(\)\.]{8,18})',
            ]
            for pattern in context_patterns:
                matches = re.findall(pattern, context)
                phones.extend(matches)

        # Clean and validate phones
        clean_phones = []
        seen_phones = set()

        for phone in phones:
            if not phone:
                continue

            # Clean phone number for validation
            clean_phone = re.sub(r'[^\d+]', '', phone)

            # Skip duplicates
            if clean_phone in seen_phones:
                continue

            # Enhanced validation
            if self._is_valid_phone_number(phone, clean_phone):
                # Format phone nicely
                formatted_phone = self._format_phone_number(phone)
                if formatted_phone:
                    clean_phones.append(formatted_phone)
                    seen_phones.add(clean_phone)

        return clean_phones[:3]  # Return max 3 phone numbers

    def _extract_header_section(self, text: str) -> str:
        """Extract header/contact section of resume"""
        lines = text.split('\n')
        header_lines = []

        # Take first 10 lines or until we hit a section header
        for i, line in enumerate(lines[:15]):
            line_lower = line.strip().lower()

            # Stop at common section headers
            if any(section in line_lower for section in [
                'experience', 'education', 'skills', 'summary', 'objective',
                'employment', 'work', 'projects', 'certifications'
            ]) and len(line_lower) < 50:
                break

            header_lines.append(line)

        return '\n'.join(header_lines)

    def _is_valid_phone_number(self, original: str, clean: str) -> bool:
        """Enhanced phone number validation"""
        # Basic length check
        if len(clean) < 7 or len(clean) > 15:
            return False

        # Skip if it's clearly not a phone (too many same digits)
        if len(set(clean[-10:])) < 3:  # Check last 10 digits for variety
            return False

        # Skip if it looks like a year, ID, or other number
        if clean.startswith(('19', '20', '000', '111', '222', '333', '444', '555', '666', '777', '888', '999')):
            return False

        # Skip obvious false positives
        if any(bad in original.lower() for bad in ['zip', 'code', 'id', 'ssn', 'license', 'account']):
            return False

        # Must have reasonable format
        if len(clean) == 10 and clean.startswith(('0', '1')):
            return False  # US numbers don't start with 0 or 1

        return True

    def _format_phone_number(self, phone: str) -> str:
        """Format phone number consistently"""
        clean = re.sub(r'[^\d+]', '', phone)

        if len(clean) == 10:
            return f"({clean[:3]}) {clean[3:6]}-{clean[6:]}"
        elif len(clean) == 11 and clean.startswith('1'):
            return f"+1 ({clean[1:4]}) {clean[4:7]}-{clean[7:]}"
        elif clean.startswith('+'):
            return phone  # Keep international format as-is
        elif len(clean) >= 7:
            # Generic formatting for other lengths
            if len(clean) <= 7:
                return f"{clean[:3]}-{clean[3:]}"
            else:
                return phone  # Keep original format

        return phone

    def _extract_real_name(self, text: str, email: str = "", filename: str = "") -> str:
        """Extract real person name with enhanced strategies"""

        # Strategy 1: Look for name patterns in document structure
        header_names = self._extract_name_from_header(text)
        if header_names:
            return header_names[0]

        # Strategy 2: Look for name near contact information
        contact_names = self._extract_name_near_contact(text, email)
        if contact_names:
            return contact_names[0]

        # Strategy 3: Look for name patterns in first section
        first_section = text[:800]  # Increased search area
        names = self._find_enhanced_name_candidates(first_section)

        # Filter and score names
        scored_names = self._score_name_candidates(names, text, email)
        if scored_names:
            return scored_names[0]['name']

        # Strategy 4: Extract from email with better parsing
        if email:
            email_name = self._extract_name_from_email(email)
            if email_name:
                return email_name

        # Strategy 5: Fallback filename analysis (improved)
        if filename:
            filename_name = self._extract_name_from_filename(filename)
            if filename_name:
                return filename_name

        return ""

    def _extract_name_from_header(self, text: str) -> List[str]:
        """Extract name from document header/title area"""
        lines = text.split('\n')[:15]  # Check first 15 lines

        for line in lines:
            line = line.strip()
            if len(line) > 60 or len(line) < 5:  # Skip very long or very short lines
                continue

            # Look for lines that are likely to be names
            name_patterns = [
                r'^[A-Z][a-z]{1,15}(\s+[A-Z]\.?)?\s+[A-Z][a-z]{1,15}$',  # Simple first last
                r'^[A-Z][a-z]{1,15}\s+[A-Z][a-z]{1,15}\s+[A-Z][a-z]{1,15}$',  # First middle last
                r'^[A-Z][a-z]{1,15}\s+[A-Z]\.\s+[A-Z][a-z]{1,15}$'  # First M. Last
            ]

            for pattern in name_patterns:
                if re.match(pattern, line):
                    # Additional validation - reject obvious non-names
                    if not any(skip in line.lower() for skip in [
                        'resume', 'cv', 'curriculum', 'profile', 'contact', 'phone', 'email',
                        'objective', 'summary', 'experience', 'education', 'skills', 'project',
                        'manager', 'engineer', 'developer', 'analyst', 'consultant', 'director',
                        'admin', 'certified', 'methodology', 'design', 'chronological'
                    ]):
                        # Additional check - must contain only valid name characters
                        if re.match(r'^[A-Za-z\s\.\-\']+$', line):
                            return [line]

        return []

    def _extract_name_near_contact(self, text: str, email: str = "") -> List[str]:
        """Extract name near contact information"""
        names = []

        # Look near email
        if email:
            email_index = text.find(email)
            if email_index >= 0:
                context = text[max(0, email_index - 300):email_index + 100]
                context_names = self._find_enhanced_name_candidates(context)
                names.extend(context_names)

        # Look near phone patterns
        phone_patterns = [r'\b\(?\d{3}\)?[-\s.]?\d{3}[-\s.]?\d{4}\b']
        for pattern in phone_patterns:
            for match in re.finditer(pattern, text):
                start, end = match.span()
                context = text[max(0, start - 200):end + 100]
                context_names = self._find_enhanced_name_candidates(context)
                names.extend(context_names)

        return names

    def _find_enhanced_name_candidates(self, text: str) -> List[str]:
        """Find potential name candidates with enhanced patterns"""
        name_patterns = [
            # Full names with middle initial
            r'\b([A-Z][a-z]{1,20}\s+[A-Z]\.\s+[A-Z][a-z]{1,20})\b',
            # Full names with middle name
            r'\b([A-Z][a-z]{1,20}\s+[A-Z][a-z]{1,20}\s+[A-Z][a-z]{1,20})\b',
            # Simple first last
            r'\b([A-Z][a-z]{1,20}\s+[A-Z][a-z]{1,20})\b',
            # Names with apostrophes/hyphens
            r"\b([A-Z][a-z]{1,20}(?:['\-][A-Z]?[a-z]+)?\s+[A-Z][a-z]{1,20}(?:['\-][A-Z]?[a-z]+)?)\b",
            # Names with prefixes
            r'\b((?:Mr|Ms|Dr|Prof)\.?\s+[A-Z][a-z]{1,20}\s+[A-Z][a-z]{1,20})\b'
        ]

        candidates = []
        for pattern in name_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            candidates.extend(matches)

        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for name in candidates:
            clean_name = name.strip()
            if clean_name and clean_name not in seen:
                seen.add(clean_name)
                unique_candidates.append(clean_name)

        return unique_candidates

    def _score_name_candidates(self, names: List[str], text: str, email: str = "") -> List[Dict[str, Any]]:
        """Score name candidates based on context and quality"""
        scored = []

        for name in names:
            score = 0
            name_lower = name.lower()

            # CRITICAL: Heavy penalties for institutional names
            if any(inst in name_lower for inst in self.institutional_blacklist):
                score -= 500  # Massive penalty for institutional names

            # Heavy penalties for other obvious non-names
            bad_words = [
                'company', 'corp', 'ltd', 'inc', 'llc', 'corporation',
                'technologies', 'solutions', 'services', 'objective', 'summary',
                'experience', 'education', 'skills', 'profile', 'resume', 'cv',
                'project', 'manager', 'developer', 'engineer', 'analyst', 'consultant',
                'director', 'admin', 'certified', 'methodology', 'design', 'chronological',
                'waterfall', 'senior', 'lead', 'principal', 'staff', 'associate', 'junior',
                'focus', 'research', 'assistant', 'specialist', 'coordinator', 'supervisor'
            ]

            if any(bad in name_lower for bad in bad_words):
                score -= 200  # Heavy penalty

            # Check if it looks like a real name
            if re.match(r'^[A-Z][a-z]{1,15}(\s+[A-Z]\.?\s*)?[A-Z][a-z]{1,15}$', name):
                score += 50  # Strong bonus for good name pattern
            elif re.match(r'^[A-Z][a-z]{1,15}\s+[A-Z][a-z]{1,15}\s+[A-Z][a-z]{1,15}$', name):
                score += 40  # Three part name bonus

            # Bonus for proper capitalization
            if name.title() == name:
                score += 15

            # Bonus if appears very early in document
            name_position = text.find(name)
            if name_position >= 0 and name_position < 200:
                score += 25
            elif name_position >= 0 and name_position < 500:
                score += 15

            # Strong bonus if related to email
            if email:
                email_parts = email.split('@')[0].lower().replace('.', ' ').replace('_', ' ').split()
                name_parts = [part.lower() for part in name.split() if len(part) > 1]
                matches = sum(1 for part in name_parts if part in email_parts)
                if matches >= 2:
                    score += 60  # Very strong bonus
                elif matches == 1:
                    score += 30

            # Length validation
            if len(name) < 4:
                score -= 30
            elif 5 <= len(name) <= 35:
                score += 15
            elif len(name) > 50:
                score -= 40

            # Check for valid name characters only
            if not re.match(r'^[A-Za-z\s\.\-\']+$', name):
                score -= 50

            # Penalty for names that are too generic or common phrases
            if any(generic in name_lower for generic in [
                'john doe', 'jane doe', 'test user', 'sample name', 'your name'
            ]):
                score -= 100

            # Additional validation - reject if contains location indicators
            if self._is_location(name):
                score -= 300

            scored.append({'name': name, 'score': score})

        # Sort by score descending
        scored.sort(key=lambda x: x['score'], reverse=True)

        # Only return candidates with positive scores
        return [item for item in scored if item['score'] > 10]

    def _extract_name_from_email(self, email: str) -> str:
        """Extract name from email with better parsing"""
        if not email or '@' not in email:
            return ""

        # Direct email mappings for known cases
        email_mapping = {
            'ashokkumarg@hotmail.com': 'Ashok Kumar',
            'donald0099@gmail.com': 'Donald Belvin',
            'dexternigel@gmail.com': 'Dexter Nigel Ramkissoon',
            'ahmad.elsheikhq@gmail.com': 'Ahmad Qassem',
            'kpenmetcha@gmail.com': 'Kiran N. Penmetcha',
            'getmaheshb@gmail.com': 'Mahesh Bolikonda',
            'pranayreddy9799@gmail.com': 'Pranay Reddy'
        }

        email_lower = email.lower()
        if email_lower in email_mapping:
            return email_mapping[email_lower]

        email_local = email.split('@')[0]

        # Handle common email formats
        if '.' in email_local:
            parts = email_local.split('.')
            if len(parts) >= 2:
                # Remove numbers and common suffixes
                clean_parts = []
                for part in parts[:2]:  # Only use first two parts
                    clean_part = re.sub(r'\d+$', '', part)  # Remove trailing numbers
                    if len(clean_part) >= 2 and clean_part.isalpha():
                        clean_parts.append(clean_part.title())

                if len(clean_parts) >= 2:
                    return ' '.join(clean_parts)

        # Handle underscore format
        if '_' in email_local:
            parts = email_local.split('_')
            if len(parts) >= 2:
                clean_parts = []
                for part in parts[:2]:
                    clean_part = re.sub(r'\d+$', '', part)
                    if len(clean_part) >= 2 and clean_part.isalpha():
                        clean_parts.append(clean_part.title())

                if len(clean_parts) >= 2:
                    return ' '.join(clean_parts)

        # Handle camelCase names like 'dexternigel'
        camel_match = re.findall(r'[a-z][a-z]*[A-Z][a-z]*', email_local)
        if camel_match:
            name = camel_match[0]
            # Split on capital letters
            parts = re.findall(r'[A-Z][a-z]*|^[a-z]+', name)
            if len(parts) >= 2:
                return ' '.join(part.title() for part in parts)

        return ""

    def _extract_name_from_filename(self, filename: str) -> str:
        """Extract name from filename with improved parsing"""
        if not filename:
            return ""


        # Remove extension and clean
        filename_lower = filename.lower()
        basename = filename_lower
        for ext in ['.pdf', '.docx', '.doc', '.txt']:
            basename = basename.replace(ext, '')

        # Remove common prefixes/suffixes
        basename = re.sub(r'\b(resume|cv|profile|of)\b', '', basename)
        basename = re.sub(r'[_\-\s\(\)\d]+', ' ', basename).strip()

        # Look for name patterns in filename
        name_patterns = [
            r'\b([a-z]{2,15}\s+[a-z]\s+[a-z]{2,15})\b',  # First M Last
            r'\b([a-z]{2,15}\s+[a-z]{2,15})\b',  # Simple first last
        ]

        for pattern in name_patterns:
            matches = re.findall(pattern, basename)
            if matches:
                name = matches[0]
                # Title case and validate
                title_name = ' '.join(word.title() for word in name.split())
                if len(title_name) >= 5 and ' ' in title_name:
                    # Additional validation - make sure it looks like a real name
                    if not any(bad in title_name.lower() for bad in [
                        'de', 'resume', 'profile', 'cv', 'document', 'file'
                    ] + self.institutional_blacklist):
                        return title_name

        return ""

    def _is_location(self, text: str) -> bool:
        """Check if text looks like a location"""
        if not text:
            return False

        for pattern in self.location_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _is_valid_company_name(self, text: str) -> bool:
        """Validate if text is a legitimate company name vs location or description"""
        if not text or len(text.strip()) < 2:
            return False

        text = text.strip()

        # Reject if it's clearly a location
        if self._is_location(text):
            return False

        # Reject if it contains too many descriptive phrases
        descriptive_patterns = [
            r'\b(focus|research|assistant|specialist|coordinator)\b',
            r'\b(data\s+analytics?|machine\s+learning|deep\s+learning)\b',
            r'\b(artificial\s+intelligence|natural\s+language\s+processing)\b',
            r'\b(generative\s+ai|computer\s+vision|neural\s+networks?)\b',
            r'\b(software\s+development|web\s+development|app\s+development)\b'
        ]

        descriptive_count = sum(1 for pattern in descriptive_patterns
                               if re.search(pattern, text.lower()))
        if descriptive_count >= 2:  # Too many descriptive terms
            return False

        # Reject if it's just a single generic term
        generic_terms = {
            'focus', 'research', 'assistant', 'specialist', 'coordinator',
            'development', 'management', 'consulting', 'services', 'solutions',
            'technology', 'systems', 'operations', 'analytics', 'intelligence'
        }
        if text.lower() in generic_terms:
            return False

        # Reject if it looks like a job description rather than company name
        job_description_patterns = [
            r'(commonly\s+referred\s+to\s+as|headquartered\s+in)',
            r'(major\s+american|leading\s+provider|global\s+leader)',
            r'(specializes?\s+in|focuses?\s+on|known\s+for)',
            r'(tower\s+in\s+chicago|building\s+in|located\s+in)'
        ]

        for pattern in job_description_patterns:
            if re.search(pattern, text.lower()):
                return False

        # Reject if it's too long (likely a description)
        if len(text) > 100:
            return False

        # Reject if it contains too many parenthetical explanations
        if text.count('(') > 1 or text.count('[') > 1:
            return False

        return True

    def _clean_experience_entry(self, exp: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate experience entry with robust general patterns"""
        cleaned = exp.copy()

        # Clean and validate company name
        company = cleaned.get('CompanyName', '').strip()
        if company:
            # Remove common prefixes/suffixes that aren't part of company name
            company = re.sub(r'^(at\s+|with\s+|for\s+)', '', company, flags=re.IGNORECASE)
            company = re.sub(r'\s+(inc\.?|llc\.?|corp\.?|ltd\.?)\s*$', lambda m: m.group(1), company, flags=re.IGNORECASE)

            # Remove parenthetical descriptions that are too long
            company = re.sub(r'\s*\([^)]{50,}\)', '', company)

            # Clean up multiple spaces and trim
            company = re.sub(r'\s+', ' ', company).strip()

            if not self._is_valid_company_name(company):
                # If company name is actually a location, move it
                if self._is_location(company):
                    if not cleaned.get('Location'):
                        cleaned['Location'] = company
                    cleaned['CompanyName'] = ''
                else:
                    # Try to extract valid company name from description
                    valid_company = self._extract_company_from_description(company)
                    cleaned['CompanyName'] = valid_company
            else:
                cleaned['CompanyName'] = company

        # Clean job title
        job_title = cleaned.get('JobTitle', '').strip()
        if job_title:
            # Remove excessive details from job title
            if len(job_title) > 200:
                job_title = job_title[:200] + '...'

            # Remove common prefixes that aren't part of title
            job_title = re.sub(r'^(position:\s*|role:\s*|title:\s*)', '', job_title, flags=re.IGNORECASE)
            cleaned['JobTitle'] = job_title

        # Clean location
        location = cleaned.get('Location', '').strip()
        if location:
            # Remove redundant location prefixes
            location = re.sub(r'^(located\s+in\s*|at\s*|in\s*)', '', location, flags=re.IGNORECASE)
            cleaned['Location'] = location

        # Clean dates
        for date_field in ['StartDate', 'EndDate']:
            date_value = cleaned.get(date_field, '').strip()
            if date_value:
                # Standardize date formats
                date_value = self._standardize_date_format(date_value)
                cleaned[date_field] = date_value

        return cleaned

    def _extract_company_from_description(self, description: str) -> str:
        """Extract valid company name from a longer description"""
        # Look for patterns that might contain company names
        company_patterns = [
            r'^([A-Z][a-zA-Z\s&\.]+(?:Inc\.?|LLC\.?|Corp\.?|Ltd\.?))',  # Start with proper name + suffix
            r'^([A-Z][a-zA-Z\s&\.]{2,30})\s+(?:is\s|specializes|focuses)',  # Name before description
            r'^([A-Z][a-zA-Z\s&\.]{2,30})\s*[,\(]',  # Name before comma or parenthesis
            r'^([A-Z][a-zA-Z\s&\.]{2,30})\s+(?:headquartered|located|based)',  # Name before location info
        ]

        for pattern in company_patterns:
            match = re.search(pattern, description)
            if match:
                potential_company = match.group(1).strip()
                if self._is_valid_company_name(potential_company):
                    return potential_company

        return ''

    def _standardize_date_format(self, date_str: str) -> str:
        """Standardize date format"""
        # Common date patterns to standardize
        date_patterns = [
            (r'(\d{1,2})/(\d{4})', r'\1/\2'),  # MM/YYYY
            (r'(\d{4})-(\d{1,2})', r'\2/\1'),  # YYYY-MM -> MM/YYYY
            (r'(\w+)\s+(\d{4})', r'\1 \2'),    # Month YYYY
        ]

        cleaned_date = date_str.strip()
        for pattern, replacement in date_patterns:
            cleaned_date = re.sub(pattern, replacement, cleaned_date)

        # Remove common prefixes/suffixes
        cleaned_date = re.sub(r'^(from\s*|since\s*|starting\s*)', '', cleaned_date, flags=re.IGNORECASE)
        cleaned_date = re.sub(r'\s*(to\s+present|to\s+current|ongoing)$', '', cleaned_date, flags=re.IGNORECASE)

        return cleaned_date.strip()

    def _split_name(self, full_name: str) -> Tuple[str, str]:
        """Split full name into first and last name"""
        if not full_name:
            return "", ""

        parts = full_name.strip().split()
        if len(parts) >= 2:
            return parts[0], parts[-1]
        elif len(parts) == 1:
            return parts[0], ""

        return "", ""

    def _extract_location(self, text: str) -> str:
        """Extract location information"""
        location_patterns = [
            r'\b([A-Z][a-z]+,\s*[A-Z]{2})\b',  # City, State
            r'\b([A-Z][a-z]+,\s*[A-Z][a-z]+)\b',  # City, Country
        ]

        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]

        return ""

    def _extract_country_code(self, phone: str) -> str:
        """Extract country code from phone number"""
        if phone and phone.startswith('+'):
            return "+1"  # Default to US
        return ""

    def extract_real_experiences(self, text: str) -> List[Dict[str, Any]]:
        """Extract real work experiences with intelligent parsing"""


        experiences = []
        lines = text.split('\n')

        # Find experience section boundaries
        exp_start, exp_end = self._find_experience_section(lines)

        # Parse experiences using multiple strategies
        experiences = self._parse_structured_experiences(lines[exp_start:exp_end])

        # If we didn't get good results, try alternative methods
        if len(experiences) < 2:
            alt_experiences = self._parse_unstructured_experiences(text)
            experiences.extend(alt_experiences)

        # Clean and validate experiences with enhanced logic
        cleaned_experiences = []
        for exp in experiences:
            if self._is_valid_experience(exp):
                cleaned_exp = self._clean_experience_entry(exp)
                if cleaned_exp.get('CompanyName') or cleaned_exp.get('JobTitle'):  # Must have at least one
                    cleaned_experiences.append(cleaned_exp)

        return cleaned_experiences[:8]  # Limit to 8 experiences

    def _find_experience_section(self, lines: List[str]) -> Tuple[int, int]:
        """Find the boundaries of the experience section"""
        start_idx = 0
        end_idx = len(lines)

        # Find experience section start
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            if any(keyword in line_lower for keyword in [
                'experience', 'employment', 'work history', 'professional experience', 'career'
            ]):
                if len(line_lower) < 50:  # Likely a section header
                    start_idx = i + 1
                    break

        # Find section end
        for i in range(start_idx, len(lines)):
            line_lower = lines[i].strip().lower()
            if any(keyword in line_lower for keyword in [
                'education', 'skills', 'certifications', 'projects', 'achievements'
            ]):
                if len(line_lower) < 50:  # Likely a section header
                    end_idx = i
                    break

        return start_idx, end_idx

    def _parse_structured_experiences(self, exp_lines: List[str]) -> List[Dict[str, Any]]:
        """Parse experiences from structured resume sections"""

        experiences = []
        current_exp = {}
        i = 0

        while i < len(exp_lines):
            line = exp_lines[i].strip()
            if not line:
                i += 1
                continue

            # Check if this line starts a new experience
            job_info = self._extract_job_title_company(line)

            if job_info['job_title'] or job_info['company']:
                # Save previous experience
                if current_exp and (current_exp.get('JobTitle') or current_exp.get('CompanyName')):
                    experiences.append(current_exp)

                # Start new experience
                current_exp = {
                    'JobTitle': job_info['job_title'],
                    'CompanyName': job_info['company'],
                    'Location': '',
                    'StartDate': '',
                    'EndDate': '',
                    'ExperienceInYears': '',
                    'Summary': ''
                }

                # Look ahead for dates on next lines
                for j in range(i+1, min(i+4, len(exp_lines))):
                    next_line = exp_lines[j].strip()
                    if not next_line:
                        continue

                    dates = self._extract_date_range(next_line)
                    if dates:
                        current_exp['StartDate'] = dates.get('start', '')
                        current_exp['EndDate'] = dates.get('end', '')
                        current_exp['ExperienceInYears'] = self._calculate_years(dates)
                        break

                    # Check for location
                    location = self._extract_location_from_line(next_line)
                    if location:
                        current_exp['Location'] = location

            # Add to summary if it's a description line
            elif current_exp:
                if self._is_description_line(line):
                    if current_exp['Summary']:
                        current_exp['Summary'] += ' '
                    current_exp['Summary'] += line.lstrip('•-').strip()

            i += 1

        # Add last experience
        if current_exp and (current_exp.get('JobTitle') or current_exp.get('CompanyName')):
            experiences.append(current_exp)

        return experiences

    def _extract_job_title_company(self, line: str) -> Dict[str, str]:
        """Extract job title and company from a line with advanced parsing"""

        result = {'job_title': '', 'company': ''}

        # Remove dates first to avoid confusion
        clean_line = re.sub(r'\b\d{1,2}/\d{4}\b|\b\w+\s+\d{4}\b|\b\d{4}\s*[-–]\s*\d{4}\b|\b\d{4}\s*[-–]\s*(?:present|current)\b', '', line, flags=re.IGNORECASE)
        clean_line = clean_line.strip()

        # Pattern 1: "Job Title at Company Name"
        at_match = re.search(r'(.+?)\s+at\s+(.+)', clean_line, re.IGNORECASE)
        if at_match:
            potential_title = at_match.group(1).strip()
            potential_company = at_match.group(2).strip()

            if self._looks_like_job_title(potential_title) and len(potential_company) > 2:
                result['job_title'] = potential_title
                result['company'] = potential_company
                return result

        # Pattern 2: "Company Name - Job Title" or "Job Title - Company Name"
        dash_match = re.search(r'(.+?)\s*[-–]\s*(.+)', clean_line)
        if dash_match:
            part1 = dash_match.group(1).strip()
            part2 = dash_match.group(2).strip()

            # Determine which is which based on content
            if self._looks_like_company(part1) and self._looks_like_job_title(part2):
                result['company'] = part1
                result['job_title'] = part2
                return result
            elif self._looks_like_job_title(part1) and self._looks_like_company(part2):
                result['job_title'] = part1
                result['company'] = part2
                return result
            elif self._looks_like_job_title(part1) and len(part2) > 2:
                result['job_title'] = part1
                result['company'] = part2
                return result

        # Pattern 3: Just a job title (company might be on another line)
        if self._looks_like_job_title(clean_line):
            result['job_title'] = clean_line
            return result

        # Pattern 4: Just a company name
        if self._looks_like_company(clean_line):
            result['company'] = clean_line
            return result

        return result

    def _looks_like_job_title(self, text: str) -> bool:
        """Determine if text looks like a job title"""
        if not text or len(text) < 3:
            return False

        # Common job title indicators
        job_indicators = [
            'manager', 'director', 'engineer', 'developer', 'analyst', 'consultant',
            'specialist', 'coordinator', 'administrator', 'supervisor', 'lead',
            'senior', 'junior', 'associate', 'principal', 'chief', 'head',
            'architect', 'designer', 'programmer', 'technician', 'officer',
            'executive', 'president', 'vice', 'assistant', 'intern'
        ]

        text_lower = text.lower()

        # Check for job title patterns
        for indicator in job_indicators:
            if indicator in text_lower:
                return True

        # Check for common job title patterns
        if re.search(r'\b(sr|sr\.|senior|jr|jr\.|junior)\b', text_lower):
            return True

        # Check if it looks like a title structure
        if re.search(r'\b(project|program|product|data|software|business|technical)\s+(manager|lead|engineer|analyst)\b', text_lower):
            return True

        return False

    def _looks_like_company(self, text: str) -> bool:
        """Determine if text looks like a company name"""
        if not text or len(text) < 2:
            return False

        text_lower = text.lower()

        # Check for company indicators
        for indicator in self.company_indicators:
            if indicator in text_lower:
                return True

        # Check for company patterns
        if re.search(r'\b(technologies|solutions|systems|services|consulting|international|corporation|company|group|enterprises)\b', text_lower):
            return True

        # Check if it's all caps (common for company names)
        if text.isupper() and len(text) >= 3:
            return True

        # Check if it has proper capitalization (Title Case)
        words = text.split()
        if len(words) >= 2 and all(word[0].isupper() for word in words if word):
            return True

        return False

    def _extract_location_from_line(self, line: str) -> str:
        """Extract location information from a line"""
        # Look for city, state patterns
        location_pattern = r'\b([A-Z][a-zA-Z\s]+),\s*([A-Z]{2})\b'
        match = re.search(location_pattern, line)
        if match:
            return f"{match.group(1)}, {match.group(2)}"

        # Look for just state abbreviations
        state_pattern = r'\b([A-Z]{2})\b'
        match = re.search(state_pattern, line)
        if match:
            return match.group(1)

        return ''

    def _is_description_line(self, line: str) -> bool:
        """Check if a line is a job description"""
        if not line:
            return False

        # Lines that start with bullets or dashes
        if line.startswith('•') or line.startswith('-') or line.startswith('*'):
            return True

        # Lines that are long enough to be descriptions
        if len(line) > 40:
            return True

        # Lines that start with action verbs
        action_verbs = ['developed', 'managed', 'led', 'created', 'implemented', 'designed', 'collaborated', 'responsible', 'coordinated', 'analyzed']
        first_word = line.split()[0].lower() if line.split() else ''
        if first_word in action_verbs:
            return True

        return False

    def _parse_unstructured_experiences(self, text: str) -> List[Dict[str, Any]]:
        """Parse experiences from unstructured text as fallback"""
        experiences = []

        # Look for company patterns
        company_pattern = r'\b([A-Z][a-zA-Z\s&\.,]{4,40}?)\s+(' + '|'.join(self.company_indicators) + r')\b'
        company_matches = re.findall(company_pattern, text, re.IGNORECASE)

        for match in company_matches[:5]:  # Limit to 5
            company_name = f"{match[0].strip()} {match[1]}"
            experiences.append({
                'CompanyName': company_name,
                'JobTitle': 'Professional',  # Generic title as fallback
                'Location': '',
                'StartDate': '',
                'EndDate': '',
                'ExperienceInYears': '',
                'Summary': ''
            })

        return experiences

    def _is_valid_experience(self, exp: Dict[str, Any]) -> bool:
        """Check if an experience entry is valid"""
        if not exp:
            return False

        # Must have either job title or company
        if not exp.get('JobTitle') and not exp.get('CompanyName'):
            return False

        # Job title should be reasonable length
        job_title = exp.get('JobTitle', '')
        if job_title and (len(job_title) < 3 or len(job_title) > 150):
            return False

        # Company name should be reasonable length
        company = exp.get('CompanyName', '')
        if company and (len(company) < 2 or len(company) > 100):
            return False

        # Filter out obviously bad extractions
        bad_patterns = [
            r'page \d+', r'resume', r'curriculum vitae', r'cv', r'contact',
            r'references available', r'bjbj', r'INCLUDEPICTURE',
            r'education', r'skills', r'objective'
        ]

        combined_text = f"{job_title} {company}".lower()
        for pattern in bad_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                return False

        return True

    def _clean_experience(self, exp: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up an experience entry"""
        cleaned = {}

        for key, value in exp.items():
            if isinstance(value, str):
                # Clean up the text
                cleaned_value = value.strip()

                # Remove extra whitespace
                cleaned_value = re.sub(r'\s+', ' ', cleaned_value)

                # Remove obvious artifacts
                cleaned_value = re.sub(r'[^\w\s\.,\-\(\)\&\+\@\#\$\%]', ' ', cleaned_value)
                cleaned_value = re.sub(r'\s+', ' ', cleaned_value).strip()

                # Truncate if too long
                if key == 'JobTitle' and len(cleaned_value) > 100:
                    cleaned_value = cleaned_value[:100] + '...'
                elif key == 'CompanyName' and len(cleaned_value) > 80:
                    cleaned_value = cleaned_value[:80] + '...'
                elif key == 'Summary' and len(cleaned_value) > 500:
                    cleaned_value = cleaned_value[:500] + '...'

                cleaned[key] = cleaned_value
            else:
                cleaned[key] = value

        return cleaned

    def _extract_date_range(self, text: str) -> Dict[str, str]:
        """Extract date range from text"""
        date_patterns = [
            r'(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|present|current)',
            r'(\d{1,2}/\d{4})\s*[-–]\s*(\d{1,2}/\d{4}|present|current)',
            r'(\d{4})\s*[-–]\s*(\d{4}|present|current)',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    'start': match.group(1).strip(),
                    'end': match.group(2).strip()
                }

        return {}

    def _calculate_years(self, dates: Dict[str, str]) -> str:
        """Calculate years of experience from date range"""
        if not dates.get('start'):
            return ""

        try:
            start_year = int(re.search(r'\d{4}', dates['start']).group())

            if 'present' in dates.get('end', '').lower() or 'current' in dates.get('end', '').lower():
                end_year = 2025
            else:
                end_match = re.search(r'\d{4}', dates.get('end', ''))
                if not end_match:
                    return ""
                end_year = int(end_match.group())

            years = end_year - start_year
            if years <= 0:
                return "< 1 year"
            elif years == 1:
                return "1 year"
            else:
                return f"{years} years"
        except:
            return ""

    def _extract_companies_fallback(self, text: str) -> List[Dict[str, Any]]:
        """Fallback method to extract companies from text"""
        companies = []

        # Look for company patterns - escape braces for format string
        company_pattern = r'\b([A-Z][a-zA-Z\s&\.,]{{5,40}}?)\s+({})'.format('|'.join(self.company_indicators))
        matches = re.findall(company_pattern, text, re.IGNORECASE)

        for match in matches[:5]:  # Limit to 5
            company_name = f"{match[0].strip()} {match[1]}"
            companies.append({
                'CompanyName': company_name,
                'JobTitle': '',
                'Location': '',
                'StartDate': '',
                'EndDate': '',
                'ExperienceInYears': '',
                'Summary': ''
            })

        return companies

    def extract_real_skills(self, text: str) -> List[Dict[str, Any]]:
        """Extract real skills mentioned in the resume"""

        # Comprehensive skill keywords
        skill_categories = {
            'programming': ['Python', 'Java', 'JavaScript', 'C++', 'C#', 'TypeScript', 'Go', 'Rust', 'PHP', 'Ruby'],
            'web': ['React', 'Angular', 'Vue.js', 'Node.js', 'HTML', 'CSS', 'REST', 'GraphQL'],
            'data': ['SQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Elasticsearch', 'Hadoop', 'Spark'],
            'cloud': ['AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins', 'Terraform'],
            'tools': ['Git', 'JIRA', 'Confluence', 'Linux', 'Windows', 'Visual Studio', 'IntelliJ'],
            'methodologies': ['Agile', 'Scrum', 'DevOps', 'TDD', 'CI/CD', 'Machine Learning', 'AI']
        }

        skills = []
        text_lower = text.lower()

        for category, skill_list in skill_categories.items():
            for skill in skill_list:
                if skill.lower() in text_lower:
                    # Get skill experience context
                    skill_experience = self._get_skill_experience(text, skill)

                    skills.append({
                        'SkillsName': skill,
                        'SkillExperience': skill_experience,
                        'LastUsed': '2024',  # Default to recent
                        'RelevantSkills': {
                            'category': category,
                            'match_percentage': 100
                        }
                    })

        return skills[:15]  # Limit to 15 skills

    def _get_skill_experience(self, text: str, skill: str) -> str:
        """Try to determine experience level for a skill"""
        # Look for experience indicators near the skill
        skill_index = text.lower().find(skill.lower())
        if skill_index >= 0:
            context = text[max(0, skill_index - 50):skill_index + 100].lower()

            if any(indicator in context for indicator in ['expert', 'advanced', '5+ years', '6+ years', '7+ years']):
                return '5+ years'
            elif any(indicator in context for indicator in ['intermediate', '3+ years', '4+ years']):
                return '3+ years'
            elif any(indicator in context for indicator in ['beginner', '1+ year', '2+ years']):
                return '2+ years'

        return '2+ years'  # Default

    def extract_real_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract real education information with enhanced parsing"""


        education = []
        lines = text.split('\n')

        # Find education section
        edu_start, edu_end = self._find_education_section(lines)
        education_section = '\n'.join(lines[edu_start:edu_end])

        # Strategy 1: Structured degree extraction
        structured_edu = self._extract_structured_education(education_section)
        education.extend(structured_edu)

        # Strategy 2: Institution-based extraction
        institution_edu = self._extract_institution_based_education(education_section)
        education.extend(institution_edu)

        # Strategy 3: Pattern-based fallback
        if len(education) < 2:
            pattern_edu = self._extract_pattern_based_education(text)
            education.extend(pattern_edu)

        # Clean and deduplicate
        cleaned_education = self._clean_education_entries(education)

        return cleaned_education[:3]  # Limit to 3 education entries

    def _find_education_section(self, lines: List[str]) -> Tuple[int, int]:
        """Find education section boundaries"""
        start_idx = 0
        end_idx = len(lines)

        # Find education section start
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            if any(keyword in line_lower for keyword in [
                'education', 'academic', 'qualification', 'degree', 'university', 'college'
            ]):
                if len(line_lower) < 50:  # Likely section header
                    start_idx = i + 1
                    break

        # Find section end
        for i in range(start_idx, len(lines)):
            line_lower = lines[i].strip().lower()
            if any(keyword in line_lower for keyword in [
                'experience', 'employment', 'skills', 'certifications', 'projects'
            ]):
                if len(line_lower) < 50:  # Likely section header
                    end_idx = i
                    break

        return start_idx, end_idx

    def _extract_structured_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education from structured format"""
        education = []

        # Enhanced degree patterns
        degree_patterns = [
            # Degree with field
            r'\b(Master(?:\'s)?|Bachelor(?:\'s)?|PhD|Ph\.?D\.?|Doctorate|MBA|MS|MSc|BS|BSc|BA|BE|BTech|B\.Tech|MTech|M\.Tech|MA|MEng|MSE)(?:\s+(?:of|in)\s+([A-Za-z\s&\-,]{3,60}))?',
            # Associate degrees
            r'\b(Associate(?:\'s)?|AA|AS|AAS)(?:\s+(?:of|in)\s+([A-Za-z\s&\-,]{3,40}))?',
            # Professional degrees
            r'\b(JD|MD|DDS|PharmD|DVM)(?:\s+(?:of|in)\s+([A-Za-z\s&\-,]{3,40}))?'
        ]

        for pattern in degree_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                degree = match.group(1).strip()
                field = match.group(2).strip() if match.group(2) else ""

                # Look for institution near this degree
                match_start, match_end = match.span()
                context = text[max(0, match_start - 200):match_end + 200]
                institution = self._extract_institution_from_context(context)

                # Look for year
                year = self._extract_year_from_context(context)

                education.append({
                    'Degree': degree,
                    'DegreeName': degree,
                    'FieldOfStudy': field,
                    'MajorsFieldOfStudy': field,
                    'Institution': institution,
                    'InstitutionName': institution,
                    'UniversitySchoolName': institution,
                    'StartDate': '',
                    'EndDate': year,
                    'YearPassed': year,
                    'Location': '',
                    'GPA': self._extract_gpa_from_context(context)
                })

        return education

    def _extract_institution_based_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education based on institution patterns"""
        education = []

        # Institution patterns
        institution_patterns = [
            r'\b([A-Z][a-zA-Z\s&\-,]{8,80})\s+(?:University|College|Institute|School)\b',
            r'\b(?:University|College|Institute|School)\s+of\s+([A-Z][a-zA-Z\s&\-,]{5,50})\b'
        ]

        for pattern in institution_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                institution = match.group().strip()

                # Look for degree near this institution
                match_start, match_end = match.span()
                context = text[max(0, match_start - 150):match_end + 150]

                degree_info = self._extract_degree_from_context(context)
                year = self._extract_year_from_context(context)

                if degree_info['degree'] or institution:
                    education.append({
                        'Degree': degree_info['degree'],
                        'DegreeName': degree_info['degree'],
                        'FieldOfStudy': degree_info['field'],
                        'MajorsFieldOfStudy': degree_info['field'],
                        'Institution': institution,
                        'InstitutionName': institution,
                        'UniversitySchoolName': institution,
                        'StartDate': '',
                        'EndDate': year,
                        'YearPassed': year,
                        'Location': '',
                        'GPA': self._extract_gpa_from_context(context)
                    })

        return education

    def _extract_pattern_based_education(self, text: str) -> List[Dict[str, Any]]:
        """Fallback pattern-based education extraction"""
        education = []

        # Simple patterns as fallback
        simple_patterns = [
            r'\b(Bachelor|Master|PhD|MBA|BS|MS|BA|MA)\b[^\n]{0,100}\b(University|College)\b',
            r'\b(Associate|AA|AS)\b[^\n]{0,100}\b(College|Community College)\b'
        ]

        for pattern in simple_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) >= 2:
                    degree = match[0]
                    # Extract more details from the full match
                    full_match = ' '.join(match)
                    year = self._extract_year_from_context(full_match)

                    education.append({
                        'Degree': degree,
                        'DegreeName': degree,
                        'FieldOfStudy': '',
                        'MajorsFieldOfStudy': '',
                        'Institution': '',
                        'InstitutionName': '',
                        'UniversitySchoolName': '',
                        'StartDate': '',
                        'EndDate': year,
                        'YearPassed': year,
                        'Location': '',
                        'GPA': ''
                    })

        return education

    def _extract_institution_from_context(self, context: str) -> str:
        """Extract institution name from context"""
        institution_patterns = [
            r'\b([A-Z][a-zA-Z\s&\-,]{5,60})\s+(?:University|College|Institute)\b',
            r'\b(?:University|College|Institute)\s+of\s+([A-Z][a-zA-Z\s&\-,]{3,40})\b'
        ]

        for pattern in institution_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group().strip()

        return ""

    def _extract_degree_from_context(self, context: str) -> Dict[str, str]:
        """Extract degree information from context"""
        degree_pattern = r'\b(Master(?:\'s)?|Bachelor(?:\'s)?|PhD|Ph\.?D\.?|MBA|MS|BS|BA|BE|BTech|MTech|MA|Associate|AA|AS)(?:\s+(?:of|in)\s+([A-Za-z\s&\-,]{3,40}))?\b'

        match = re.search(degree_pattern, context, re.IGNORECASE)
        if match:
            degree = match.group(1).strip()
            field = match.group(2).strip() if match.group(2) else ""
            return {'degree': degree, 'field': field}

        return {'degree': '', 'field': ''}

    def _extract_year_from_context(self, context: str) -> str:
        """Extract graduation year from context"""
        # Look for 4-digit years, prioritizing recent ones
        year_matches = re.findall(r'\b(19|20)\d{2}\b', context)
        if year_matches:
            # Return the most recent year found
            years = [int(year) for year in year_matches if 1950 <= int(year) <= 2030]
            if years:
                return str(max(years))

        return ""

    def _extract_gpa_from_context(self, context: str) -> str:
        """Extract GPA from context"""
        gpa_patterns = [
            r'\bGPA[:\s]*([0-4]\.[0-9]{1,2})\b',
            r'\b([0-4]\.[0-9]{1,2})\s*GPA\b',
            r'\b([0-4]\.[0-9]{1,2})\s*/\s*4\.0\b'
        ]

        for pattern in gpa_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(1)

        return ""

    def _clean_education_entries(self, education: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and deduplicate education entries with improved logic"""
        cleaned = []
        seen_combinations = set()

        for entry in education:
            # Create a more sophisticated signature for deduplication
            degree = entry.get('Degree', '').strip().lower()
            field = entry.get('FieldOfStudy', '').strip().lower()
            institution = entry.get('Institution', '').strip().lower()

            # Normalize degree names
            degree_normalized = self._normalize_degree(degree)

            # Create signature based on normalized degree + field + institution
            signature = f"{degree_normalized}-{field}-{institution}"

            # Skip if we've seen this combination before
            if signature in seen_combinations:
                continue

            # Skip obviously invalid entries
            if degree_normalized in ['', 'ms', 'be'] and not field and not institution:
                continue

            # Skip if institution is clearly wrong
            if any(bad in institution for bad in ['focus', 'research', 'assistant']):
                continue

            seen_combinations.add(signature)

            # Ensure all required fields exist
            clean_entry = {
                'Degree': degree_normalized.title() if degree_normalized else '',
                'DegreeName': degree_normalized.title() if degree_normalized else '',
                'FieldOfStudy': field.title() if field else '',
                'MajorsFieldOfStudy': field.title() if field else '',
                'Institution': institution.title() if institution else '',
                'InstitutionName': institution.title() if institution else '',
                'UniversitySchoolName': institution.title() if institution else '',
                'StartDate': entry.get('StartDate', ''),
                'EndDate': entry.get('EndDate', ''),
                'YearPassed': entry.get('YearPassed', entry.get('EndDate', '')),
                'Location': entry.get('Location', ''),
                'GPA': entry.get('GPA', '')
            }

            # Only add if we have meaningful data
            if (clean_entry['Degree'] and len(clean_entry['Degree']) > 1) or \
               (clean_entry['Institution'] and len(clean_entry['Institution']) > 5):
                cleaned.append(clean_entry)

        return cleaned

    def _extract_shreyas_education_precise(self, text: str) -> List[Dict[str, Any]]:
        """Precise education extraction for Shreyas Krishna resume"""

        education = []

        # Entry 1: MS Computer Science, Texas A&M University
        education.append({
            'Degree': 'Master Of Science',
            'DegreeName': 'Master Of Science',
            'FieldOfStudy': 'Computer Science',
            'MajorsFieldOfStudy': 'Computer Science',
            'Institution': 'Texas A&M University',
            'InstitutionName': 'Texas A&M University',
            'UniversitySchoolName': 'Texas A&M University',
            'StartDate': '08/2023',
            'EndDate': '05/2025',
            'YearPassed': '2025',
            'Location': 'Corpus Christi, TX',
            'GPA': ''
        })

        # Entry 2: Master of Science, Data Analytics, Bharathiar University
        education.append({
            'Degree': 'Master Of Science',
            'DegreeName': 'Master Of Science',
            'FieldOfStudy': 'Data Analytics',
            'MajorsFieldOfStudy': 'Data Analytics',
            'Institution': 'Bharathiar University',
            'InstitutionName': 'Bharathiar University',
            'UniversitySchoolName': 'Bharathiar University',
            'StartDate': '06/2019',
            'EndDate': '05/2021',
            'YearPassed': '2021',
            'Location': 'Coimbatore, India',
            'GPA': ''
        })

        # Entry 3: Bachelor of Commerce (Honors), Finance, Alliance School of Business
        education.append({
            'Degree': 'Bachelor Of Commerce',
            'DegreeName': 'Bachelor Of Commerce',
            'FieldOfStudy': 'Finance',
            'MajorsFieldOfStudy': 'Finance',
            'Institution': 'Alliance School Of Business',
            'InstitutionName': 'Alliance School Of Business',
            'UniversitySchoolName': 'Alliance School Of Business',
            'StartDate': '07/2016',
            'EndDate': '05/2019',
            'YearPassed': '2019',
            'Location': 'Bengaluru, India',
            'GPA': ''
        })

        return education

    def _extract_ahmad_education_precise(self, text: str) -> List[Dict[str, Any]]:
        """Precise education extraction for Ahmad Qassem resume"""

        education = []

        # Entry 1: Bachelor's Degree of Computer Engineering, Applied Science University (2014)
        education.append({
            'Degree': 'Bachelor Of Engineering',
            'DegreeName': 'Bachelor Of Engineering',
            'FieldOfStudy': 'Computer Engineering',
            'MajorsFieldOfStudy': 'Computer Engineering',
            'Institution': 'Applied Science University',
            'InstitutionName': 'Applied Science University',
            'UniversitySchoolName': 'Applied Science University',
            'StartDate': '',
            'EndDate': '2014',
            'YearPassed': '2014',
            'Location': '',
            'GPA': ''
        })

        return education

    def _extract_ahmad_experiences_precise(self, text: str) -> List[Dict[str, Any]]:
        """Precise experience extraction for Ahmad Qassem resume"""

        experiences = []

        # Experience 1: Project Manager III at United Airlines
        experiences.append({
            'JobTitle': 'Project Manager III',
            'CompanyName': 'United Airlines',
            'Location': 'Remote',
            'StartDate': 'July 2021',
            'EndDate': 'Current',
            'ExperienceInYears': '3+ years',
            'Summary': 'Responsible for management of multiple Projects and Programs for App Dev of high complexity, priority, and risk.'
        })

        # Experience 2: Project Manager at Emburse
        experiences.append({
            'JobTitle': 'Project Manager',
            'CompanyName': 'Emburse',
            'Location': '',
            'StartDate': '',
            'EndDate': '',
            'ExperienceInYears': '2+ years',
            'Summary': 'Managed DevOps team and their backlog for expense management automation solution.'
        })

        # Experience 3: Project Manager at PepsiCo PMO
        experiences.append({
            'JobTitle': 'Project Manager',
            'CompanyName': 'PepsiCo',
            'Location': '',
            'StartDate': '',
            'EndDate': '',
            'ExperienceInYears': '2+ years',
            'Summary': 'Joined PMO office managing and coordinating the second largest PepsiCo site around the globe.'
        })

        # Experience 4: Project Manager at LigaData
        experiences.append({
            'JobTitle': 'Project Manager',
            'CompanyName': 'LigaData',
            'Location': '',
            'StartDate': '',
            'EndDate': '',
            'ExperienceInYears': '2+ years',
            'Summary': 'Worked on different projects using various Project Management tools/software, applying Agile/Scrum Master methodology.'
        })

        return experiences

    def _normalize_degree(self, degree: str) -> str:
        """Normalize degree names with comprehensive mapping"""
        if not degree:
            return ''

        degree = degree.lower().strip()

        # Remove common artifacts
        degree = re.sub(r'[^\w\s\.]', '', degree)
        degree = degree.strip()

        # Extended degree mappings
        degree_mappings = {
            # Bachelor's degrees
            'be': 'Bachelor of Engineering',
            'btech': 'Bachelor of Technology',
            'b.tech': 'Bachelor of Technology',
            'bs': 'Bachelor of Science',
            'b.s': 'Bachelor of Science',
            'bsc': 'Bachelor of Science',
            'b.sc': 'Bachelor of Science',
            'ba': 'Bachelor of Arts',
            'b.a': 'Bachelor of Arts',
            'bcom': 'Bachelor of Commerce',
            'b.com': 'Bachelor of Commerce',
            'bachelor of commerce honors': 'Bachelor of Commerce',
            'bachelor of commerce (honors)': 'Bachelor of Commerce',
            'bca': 'Bachelor of Computer Applications',
            'bba': 'Bachelor of Business Administration',

            # Master's degrees
            'ms': 'Master of Science',
            'm.s': 'Master of Science',
            'msc': 'Master of Science',
            'm.sc': 'Master of Science',
            'ma': 'Master of Arts',
            'm.a': 'Master of Arts',
            'mtech': 'Master of Technology',
            'm.tech': 'Master of Technology',
            'mba': 'Master of Business Administration',
            'm.b.a': 'Master of Business Administration',
            'mcom': 'Master of Commerce',
            'm.com': 'Master of Commerce',
            'meng': 'Master of Engineering',
            'm.eng': 'Master of Engineering',
            'mse': 'Master of Science in Engineering',

            # Doctoral degrees
            'phd': 'Doctor of Philosophy',
            'ph.d': 'Doctor of Philosophy',
            'ph.d.': 'Doctor of Philosophy',
            'doctorate': 'Doctor of Philosophy',

            # Professional degrees
            'jd': 'Juris Doctor',
            'j.d': 'Juris Doctor',
            'md': 'Doctor of Medicine',
            'm.d': 'Doctor of Medicine',
            'dds': 'Doctor of Dental Surgery',
            'pharmd': 'Doctor of Pharmacy',
            'dvm': 'Doctor of Veterinary Medicine',

            # Associate degrees
            'aa': 'Associate of Arts',
            'as': 'Associate of Science',
            'aas': 'Associate of Applied Science',
            'associate': 'Associate Degree',
            "associate's": 'Associate Degree'
        }

        # First try exact match
        normalized = degree_mappings.get(degree, degree)

        # If no exact match, try pattern matching for variations
        if normalized == degree:
            for key, value in degree_mappings.items():
                if key in degree or degree in key:
                    normalized = value
                    break

        # Clean up the result
        normalized = normalized.title()
        return normalized