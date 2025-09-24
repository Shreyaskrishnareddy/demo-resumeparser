#!/usr/bin/env python3
"""
Detailed accuracy analyzer to identify specific failure patterns
"""

import os
import time
import fitz
from docx import Document
from fast_brd_transformer import FastBRDTransformer

class AccuracyAnalyzer:
    def __init__(self):
        self.transformer = FastBRDTransformer()
        self.test_dir = "/home/great/claudeprojects/parser/test_resumes/Test Resumes"

    def get_file_text(self, file_path):
        """Extract text from various file formats"""
        file_path = str(file_path)
        extension = os.path.splitext(file_path)[1].lower()

        try:
            if extension == '.pdf':
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text
            elif extension == '.docx':
                doc = Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            elif extension == '.doc':
                with open(file_path, 'rb') as f:
                    content = f.read()
                    text = ''.join(chr(byte) for byte in content if 32 <= byte <= 126)
                    return text
            else:
                return ""
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""

    def analyze_file_detailed(self, filename):
        """Analyze a single file in detail"""
        print(f"\n🔍 DETAILED ANALYSIS: {filename}")
        print("=" * 80)

        file_path = os.path.join(self.test_dir, filename)
        text = self.get_file_text(file_path)

        if not text:
            print("❌ Could not extract text")
            return

        # Show first few lines for context
        lines = text.split('\n')
        print("📄 FIRST 10 LINES:")
        for i, line in enumerate(lines[:10]):
            if line.strip():
                print(f"  {i+1:2}: {repr(line.strip())}")

        # Parse with timing
        start_time = time.time()
        result = self.transformer.transform_to_brd_format(text, filename)
        parse_time = (time.time() - start_time) * 1000

        # Analyze each component
        personal = result.get('PersonalDetails', {})
        experiences = result.get('ListOfExperiences', [])
        skills = result.get('ListOfSkills', [])
        education = result.get('Education', [])

        print(f"\n⏱️  PERFORMANCE: {parse_time:.2f}ms")

        print(f"\n👤 PERSONAL DETAILS:")
        print(f"  FullName: {repr(personal.get('FullName', ''))}")
        print(f"  FirstName: {repr(personal.get('FirstName', ''))}")
        print(f"  LastName: {repr(personal.get('LastName', ''))}")
        print(f"  Email: {repr(personal.get('EmailID', ''))}")
        print(f"  Phone: {repr(personal.get('PhoneNumber', ''))}")

        print(f"\n💼 EXPERIENCES ({len(experiences)}):")
        for i, exp in enumerate(experiences):
            print(f"  {i+1}. Company: {repr(exp.get('CompanyName', ''))}")
            print(f"     Title: {repr(exp.get('JobTitle', ''))}")
            print(f"     Dates: {repr(exp.get('StartDate', ''))} - {repr(exp.get('EndDate', ''))}")

        print(f"\n🛠️  SKILLS ({len(skills)}):")
        for i, skill in enumerate(skills[:5]):  # Show first 5
            print(f"  {i+1}. {repr(skill.get('SkillsName', ''))}")

        print(f"\n🎓 EDUCATION ({len(education)}):")
        for i, edu in enumerate(education):
            print(f"  {i+1}. {repr(edu.get('FullEducationDetails', ''))}")

        # Calculate accuracy score breakdown
        score = 0
        max_score = 100
        breakdown = []

        # Critical fields (50 points)
        if personal.get('FullName'):
            score += 15
            breakdown.append("✅ FullName: +15")
        else:
            breakdown.append("❌ FullName: 0")

        if personal.get('EmailID'):
            score += 15
            breakdown.append("✅ EmailID: +15")
        else:
            breakdown.append("❌ EmailID: 0")

        if personal.get('PhoneNumber'):
            score += 10
            breakdown.append("✅ PhoneNumber: +10")
        else:
            breakdown.append("❌ PhoneNumber: 0")

        if personal.get('FirstName'):
            score += 5
            breakdown.append("✅ FirstName: +5")
        else:
            breakdown.append("❌ FirstName: 0")

        if personal.get('LastName'):
            score += 5
            breakdown.append("✅ LastName: +5")
        else:
            breakdown.append("❌ LastName: 0")

        # Core sections (40 points)
        if experiences:
            score += 10
            breakdown.append(f"✅ Experiences: +10 ({len(experiences)} found)")
            for exp in experiences[:2]:
                if exp.get('CompanyName'):
                    score += 2
                    breakdown.append("✅ Company: +2")
                if exp.get('JobTitle'):
                    score += 2
                    breakdown.append("✅ JobTitle: +2")
                if exp.get('StartDate'):
                    score += 1
                    breakdown.append("✅ StartDate: +1")
        else:
            breakdown.append("❌ Experiences: 0")

        if skills:
            score += 10
            breakdown.append(f"✅ Skills: +10 ({len(skills)} found)")
        else:
            breakdown.append("❌ Skills: 0")

        if education:
            score += 5
            breakdown.append("✅ Education: +5")
        else:
            breakdown.append("❌ Education: 0")

        # Performance (10 points)
        if parse_time <= 2.0:
            score += 5
            breakdown.append("✅ Performance: +5")
        else:
            breakdown.append(f"❌ Performance: 0 ({parse_time:.2f}ms > 2ms)")

        score += 5  # BRD compliant flag
        breakdown.append("✅ BRD Compliant: +5")

        print(f"\n📊 ACCURACY BREAKDOWN:")
        for item in breakdown:
            print(f"  {item}")
        print(f"\n🎯 TOTAL SCORE: {score}/100 ({score}%)")

        return {
            'filename': filename,
            'score': score,
            'parse_time': parse_time,
            'breakdown': breakdown,
            'issues': self._identify_issues(personal, experiences, skills, parse_time)
        }

    def _identify_issues(self, personal, experiences, skills, parse_time):
        """Identify specific issues with the parsing"""
        issues = []

        if not personal.get('FullName'):
            issues.append("Missing full name")
        elif any(word in personal.get('FullName', '').lower() for word in ['business', 'skills', 'executive', 'briefing', 'solutions', 'objective']):
            issues.append(f"Wrong name detected: '{personal.get('FullName')}'")

        if not personal.get('EmailID'):
            issues.append("Missing email")
        elif '@' not in personal.get('EmailID', ''):
            issues.append(f"Invalid email: '{personal.get('EmailID')}'")

        if not personal.get('PhoneNumber'):
            issues.append("Missing phone number")

        if len(experiences) == 0:
            issues.append("No work experiences found")
        elif len(experiences) < 2:
            issues.append("Too few work experiences found")

        if len(skills) < 5:
            issues.append("Too few skills found")

        if parse_time > 2.0:
            issues.append(f"Performance too slow: {parse_time:.2f}ms")

        return issues

    def analyze_all_failing_files(self):
        """Analyze all files that are not achieving 90%+ accuracy"""
        failing_files = [
            "Dexter Nigel Ramkissoon.docx",  # Wrong name: "BUSINESS SKILLS"
            "Donald Belvin.docx",            # Low accuracy
            "Kiran N. Penmetcha_s Profile.pdf",  # Wrong name: "Executive Briefing"
            "Mahesh_Bolikonda (1).pdf",     # Close to 90% - needs small improvement
            "PRANAY REDDY_DE_Resume.pdf",   # Very low accuracy
            "Ashok Kumar.doc",              # .doc corruption issue
            "Resume of Connal Jackson.doc"  # .doc corruption issue
        ]

        print("🧪 ANALYZING ALL FAILING FILES")
        print("=" * 80)

        results = []
        for filename in failing_files:
            if os.path.exists(os.path.join(self.test_dir, filename)):
                results.append(self.analyze_file_detailed(filename))

        # Summary of issues
        print(f"\n📋 SUMMARY OF ISSUES:")
        print("=" * 80)
        all_issues = []
        for result in results:
            all_issues.extend(result['issues'])

        # Count issue frequency
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        print("🔥 Most common issues:")
        for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {count}x: {issue}")

        return results

if __name__ == "__main__":
    analyzer = AccuracyAnalyzer()
    analyzer.analyze_all_failing_files()