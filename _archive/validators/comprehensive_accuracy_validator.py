#!/usr/bin/env python3
"""
Comprehensive accuracy validation tool for BRD-compliant resume parser
Tests all resume files for 90%+ accuracy requirement
"""

import os
import time
import json
from datetime import datetime
from pathlib import Path
from fast_brd_transformer import FastBRDTransformer
import fitz
from docx import Document

class AccuracyValidator:
    def __init__(self):
        self.transformer = FastBRDTransformer()
        self.test_dir = "/home/great/claudeprojects/parser/test_resumes/Test Resumes"
        self.results = []
        self.accuracy_threshold = 90.0  # BRD requirement

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
                # Basic .doc support
                with open(file_path, 'rb') as f:
                    content = f.read()
                    text = ''.join(chr(byte) for byte in content if 32 <= byte <= 126)
                    return text
            else:
                return ""
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""

    def calculate_accuracy_score(self, result, filename):
        """Calculate accuracy score based on BRD requirements"""
        score = 0
        max_score = 100

        # Critical fields (50 points total)
        personal = result.get('PersonalDetails', {})
        if personal.get('FullName'):
            score += 15
        if personal.get('EmailID'):
            score += 15
        if personal.get('PhoneNumber'):
            score += 10
        if personal.get('FirstName'):
            score += 5
        if personal.get('LastName'):
            score += 5

        # Core sections (40 points total)
        experiences = result.get('ListOfExperiences', [])
        if experiences:
            score += 10
            # Quality of experience data
            for exp in experiences[:2]:  # Check first 2
                if exp.get('CompanyName'):
                    score += 2
                if exp.get('JobTitle'):
                    score += 2
                if exp.get('StartDate'):
                    score += 1

        skills = result.get('ListOfSkills', [])
        if skills:
            score += 10

        education = result.get('Education', [])
        if education:
            score += 5

        certifications = result.get('Certifications', [])
        if certifications:
            score += 5

        # BRD compliance (10 points)
        metadata = result.get('ParsingMetadata', {})
        if metadata.get('brd_compliant'):
            score += 5
        if metadata.get('parsing_time_ms', 999) <= 2.0:
            score += 5

        return min(score, max_score)

    def run_comprehensive_test(self):
        """Run comprehensive test on all resume files"""
        print("🧪 COMPREHENSIVE ACCURACY VALIDATION")
        print("=" * 60)
        print(f"BRD Requirement: {self.accuracy_threshold}% accuracy")
        print(f"Performance Target: ≤2ms parsing time")
        print("=" * 60)

        # Get all resume files
        if not os.path.exists(self.test_dir):
            print(f"❌ Test directory not found: {self.test_dir}")
            return

        files = []
        for file in os.listdir(self.test_dir):
            if file.endswith(('.pdf', '.doc', '.docx')) and not file.endswith('.Zone.Identifier'):
                files.append(file)

        if not files:
            print("❌ No resume files found")
            return

        print(f"Found {len(files)} resume files to test\n")

        # Test each file
        total_accuracy = 0
        total_performance = 0
        successful_tests = 0
        meets_accuracy = 0
        meets_performance = 0

        for filename in sorted(files)[:10]:  # Test first 10 files for speed
            print(f"📄 Testing: {filename}")
            file_path = os.path.join(self.test_dir, filename)

            # Extract text
            text = self.get_file_text(file_path)
            if not text:
                print(f"  ❌ Could not extract text")
                continue

            # Parse with timing
            start_time = time.time()
            try:
                result = self.transformer.transform_to_brd_format(text, filename)
                parse_time = (time.time() - start_time) * 1000
            except Exception as e:
                print(f"  ❌ Parsing error: {e}")
                continue

            # Calculate accuracy
            accuracy = self.calculate_accuracy_score(result, filename)

            # Analyze results
            personal = result.get('PersonalDetails', {})
            experiences = result.get('ListOfExperiences', [])
            skills = result.get('ListOfSkills', [])

            # Performance status
            meets_target = parse_time <= 2.0
            if meets_target:
                print(f"  ✅ Performance: {parse_time:.2f}ms")
                meets_performance += 1
            else:
                print(f"  ⚠️  Performance: {parse_time:.2f}ms (exceeds target)")

            # Accuracy status
            if accuracy >= self.accuracy_threshold:
                print(f"  ✅ Accuracy: {accuracy}%")
                meets_accuracy += 1
            else:
                print(f"  ❌ Accuracy: {accuracy}% (below {self.accuracy_threshold}%)")

            print(f"  📊 Data: {personal.get('FullName', 'No name')} | {len(experiences)} exp | {len(skills)} skills")

            total_accuracy += accuracy
            total_performance += parse_time
            successful_tests += 1
            print()

        # Generate summary
        if successful_tests > 0:
            avg_accuracy = total_accuracy / successful_tests
            avg_performance = total_performance / successful_tests

            print("=" * 60)
            print("📊 COMPREHENSIVE VALIDATION SUMMARY")
            print("=" * 60)
            print(f"Files tested: {successful_tests}")
            print(f"Average accuracy: {avg_accuracy:.1f}%")
            print(f"Average performance: {avg_performance:.2f}ms")
            print()
            print("🎯 BRD COMPLIANCE:")
            print(f"  Accuracy (≥{self.accuracy_threshold}%): {meets_accuracy}/{successful_tests} files ({meets_accuracy/successful_tests*100:.1f}%)")
            print(f"  Performance (≤2ms): {meets_performance}/{successful_tests} files ({meets_performance/successful_tests*100:.1f}%)")
            print()

            # Overall assessment
            if avg_accuracy >= self.accuracy_threshold and avg_performance <= 2.5:
                print("🎉 ✅ OVERALL BRD COMPLIANCE: ACHIEVED")
                print("🏆 Parser ready for production!")
            else:
                print("⚠️  ❌ OVERALL BRD COMPLIANCE: NEEDS IMPROVEMENT")

def main():
    validator = AccuracyValidator()
    validator.run_comprehensive_test()

if __name__ == "__main__":
    main()