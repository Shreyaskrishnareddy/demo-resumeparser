#!/usr/bin/env python3
"""
RIGOROUS RESUME PARSER TEST SUITE
Comprehensive testing of all resume files with detailed analysis
"""

import os
import time
import json
from datetime import datetime
from pathlib import Path
import traceback
from fixed_resume_parser import FixedResumeParser
import fitz  # PyMuPDF
import docx

class RigorousTestSuite:
    def __init__(self):
        self.test_dir = "/home/great/claudeprojects/parser/test_resumes/Test Resumes"
        self.parser = FixedResumeParser()
        self.results = []
        self.total_files = 0
        self.successful_parses = 0
        self.failed_parses = 0

    def extract_text_from_file(self, file_path, filename):
        """Extract text from various file formats"""
        try:
            file_ext = Path(filename).suffix.lower()

            if file_ext == '.pdf':
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text, "success"

            elif file_ext in ['.docx', '.doc']:
                try:
                    doc = docx.Document(file_path)
                    text = ""
                    for paragraph in doc.paragraphs:
                        text += paragraph.text + "\n"
                    return text, "success"
                except Exception as e:
                    return f"Error reading document: {str(e)}", "error"

            else:
                return f"Unsupported format: {file_ext}", "error"

        except Exception as e:
            return f"Extraction error: {str(e)}", "error"

    def analyze_contact_info(self, contact_info):
        """Analyze quality of extracted contact information"""
        issues = []
        scores = {'name': 0, 'email': 0, 'phone': 0, 'location': 0}

        # Name analysis
        name = contact_info.get('CandidateName', {}).get('FormattedName', '')
        if not name:
            issues.append("❌ No name extracted")
        elif len(name) < 2:
            issues.append("❌ Name too short")
            scores['name'] = 20
        elif len(name) > 100:
            issues.append("⚠️ Name too long (likely contains certifications)")
            scores['name'] = 60
        elif any(word in name.lower() for word in ['file', 'document', 'resume', 'cv']):
            issues.append("❌ Name contains document artifacts")
            scores['name'] = 30
        else:
            scores['name'] = 100

        # Email analysis
        emails = contact_info.get('EmailAddresses', [])
        if not emails:
            issues.append("❌ No email found")
        elif '@' not in emails[0].get('Address', ''):
            issues.append("❌ Invalid email format")
            scores['email'] = 30
        else:
            scores['email'] = 100

        # Phone analysis
        phones = contact_info.get('Telephones', [])
        if not phones:
            issues.append("❌ No phone number found")
        else:
            phone = phones[0].get('Raw', '')
            if len(phone) < 10:
                issues.append("⚠️ Phone number seems incomplete")
                scores['phone'] = 70
            else:
                scores['phone'] = 100

        # Location analysis
        location = contact_info.get('Location', {})
        if not location.get('Municipality') and not location.get('Region'):
            issues.append("⚠️ No location information")
        else:
            scores['location'] = 100

        overall_score = sum(scores.values()) / len(scores)
        return issues, scores, overall_score

    def analyze_experience(self, employment_history):
        """Analyze quality of experience extraction"""
        issues = []
        positions = employment_history.get('Positions', [])

        if not positions:
            issues.append("❌ No positions found")
            return issues, 0, {'valid_positions': 0, 'invalid_positions': 0}

        valid_positions = 0
        invalid_positions = 0

        for i, pos in enumerate(positions):
            company = pos.get('Employer', {}).get('Name', '')
            title = pos.get('JobTitle', '')
            dates = pos.get('Dates', '')

            # Check if this looks like a valid position
            is_valid = True

            # Company name checks
            if not company or len(company) < 3:
                is_valid = False
                issues.append(f"Position {i+1}: Invalid company name '{company}'")
            elif company.lower().startswith(('implement', 'develop', 'manage', 'perform', 'establish', 'architect', 'client:', 'worked', 'served', 'responsible')):
                is_valid = False
                issues.append(f"Position {i+1}: Company name is actually a job description: '{company}'")

            # Title checks
            if title and len(title) > 100:
                is_valid = False
                issues.append(f"Position {i+1}: Job title too long (likely description): '{title[:50]}...'")

            if is_valid:
                valid_positions += 1
            else:
                invalid_positions += 1

        # Overall assessment
        total_positions = len(positions)
        if total_positions > 10:
            issues.append(f"⚠️ Unusually high position count ({total_positions}) - likely over-detection")
        elif total_positions < 2:
            issues.append(f"⚠️ Very few positions found ({total_positions}) - possible under-detection")

        position_quality_score = (valid_positions / total_positions * 100) if total_positions > 0 else 0

        return issues, position_quality_score, {
            'total_positions': total_positions,
            'valid_positions': valid_positions,
            'invalid_positions': invalid_positions
        }

    def analyze_skills(self, skills):
        """Analyze quality of skills extraction"""
        issues = []

        if not skills:
            issues.append("❌ No skills found")
            return issues, 0

        skill_count = len(skills)

        if skill_count < 5:
            issues.append(f"⚠️ Very few skills found ({skill_count})")
            score = 50
        elif skill_count > 30:
            issues.append(f"⚠️ Too many skills found ({skill_count}) - possible noise")
            score = 70
        else:
            score = 100

        return issues, score

    def calculate_brd_compliance(self, result, performance_time):
        """Calculate BRD compliance based on accuracy and performance"""
        contact_info = result.get('ContactInformation', {})
        employment = result.get('EmploymentHistory', {})
        skills = result.get('Skills', [])

        # Contact info score (40% weight)
        contact_issues, contact_scores, contact_overall = self.analyze_contact_info(contact_info)

        # Experience score (40% weight)
        exp_issues, exp_score, exp_stats = self.analyze_experience(employment)

        # Skills score (20% weight)
        skill_issues, skill_score = self.analyze_skills(skills)

        # Calculate weighted accuracy
        accuracy = (contact_overall * 0.4) + (exp_score * 0.4) + (skill_score * 0.2)

        # Performance check (target: <2ms)
        performance_ok = performance_time < 0.002

        # BRD compliance (90% accuracy + 2ms performance)
        brd_compliant = accuracy >= 90 and performance_ok

        return {
            'accuracy': accuracy,
            'performance_ok': performance_ok,
            'brd_compliant': brd_compliant,
            'contact_score': contact_overall,
            'experience_score': exp_score,
            'skills_score': skill_score,
            'all_issues': contact_issues + exp_issues + skill_issues,
            'experience_stats': exp_stats
        }

    def test_single_file(self, filename):
        """Test a single resume file"""
        file_path = os.path.join(self.test_dir, filename)

        print(f"\n🧪 Testing: {filename}")
        print("-" * 60)

        start_time = time.time()

        # Extract text
        text, extraction_status = self.extract_text_from_file(file_path, filename)

        if extraction_status == "error":
            print(f"❌ Text extraction failed: {text}")
            return {
                'filename': filename,
                'status': 'failed',
                'error': text,
                'extraction_time': time.time() - start_time
            }

        print(f"✅ Text extracted ({len(text)} chars)")

        # Parse resume
        try:
            parsing_start = time.time()
            result = self.parser.parse_resume(text, filename)
            parsing_time = time.time() - parsing_start
            total_time = time.time() - start_time

            print(f"✅ Parsing completed ({parsing_time:.3f}s)")

            # Analyze results
            analysis = self.calculate_brd_compliance(result, parsing_time)

            # Extract key metrics
            contact = result.get('ContactInformation', {})
            name = contact.get('CandidateName', {}).get('FormattedName', 'NOT FOUND')
            email = (contact.get('EmailAddresses', [{}])[0].get('Address', 'NOT FOUND')
                    if contact.get('EmailAddresses') else 'NOT FOUND')
            phone = (contact.get('Telephones', [{}])[0].get('Raw', 'NOT FOUND')
                    if contact.get('Telephones') else 'NOT FOUND')

            positions = result.get('EmploymentHistory', {}).get('Positions', [])
            skills = result.get('Skills', [])

            # Display results
            print(f"\n📊 RESULTS:")
            print(f"  👤 Name: {name[:50]}{'...' if len(name) > 50 else ''}")
            print(f"  📧 Email: {email}")
            print(f"  📞 Phone: {phone}")
            print(f"  💼 Positions: {len(positions)}")
            print(f"  🛠️  Skills: {len(skills)}")
            print(f"  ⏱️  Processing Time: {parsing_time:.3f}s")
            print(f"  📈 Overall Accuracy: {analysis['accuracy']:.1f}%")
            print(f"  🎯 BRD Compliant: {'✅' if analysis['brd_compliant'] else '❌'}")

            # Show issues
            if analysis['all_issues']:
                print(f"\n🚨 Issues Found ({len(analysis['all_issues'])}):")
                for issue in analysis['all_issues'][:5]:  # Show top 5 issues
                    print(f"  {issue}")
                if len(analysis['all_issues']) > 5:
                    print(f"  ... and {len(analysis['all_issues']) - 5} more issues")

            return {
                'filename': filename,
                'status': 'success',
                'name': name,
                'email': email,
                'phone': phone,
                'positions_count': len(positions),
                'skills_count': len(skills),
                'parsing_time': parsing_time,
                'total_time': total_time,
                'accuracy': analysis['accuracy'],
                'contact_score': analysis['contact_score'],
                'experience_score': analysis['experience_score'],
                'skills_score': analysis['skills_score'],
                'brd_compliant': analysis['brd_compliant'],
                'issues': analysis['all_issues'],
                'experience_stats': analysis['experience_stats'],
                'performance_ok': analysis['performance_ok']
            }

        except Exception as e:
            error_msg = f"Parsing error: {str(e)}"
            print(f"❌ {error_msg}")
            print(f"Stack trace: {traceback.format_exc()}")

            return {
                'filename': filename,
                'status': 'failed',
                'error': error_msg,
                'parsing_time': time.time() - parsing_start,
                'total_time': time.time() - start_time
            }

    def run_comprehensive_test(self):
        """Run tests on all resume files"""
        print("🧪 RIGOROUS RESUME PARSER TEST SUITE")
        print("=" * 80)
        print(f"Test Directory: {self.test_dir}")
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        # Get all resume files (exclude Zone.Identifier files)
        files = [f for f in os.listdir(self.test_dir)
                if not f.endswith('.Zone.Identifier') and
                os.path.isfile(os.path.join(self.test_dir, f))]

        self.total_files = len(files)
        print(f"📁 Found {self.total_files} resume files to test")

        # Test each file
        for i, filename in enumerate(files, 1):
            print(f"\n{'='*60}")
            print(f"📄 TEST {i}/{self.total_files}")
            print(f"{'='*60}")

            result = self.test_single_file(filename)
            self.results.append(result)

            if result['status'] == 'success':
                self.successful_parses += 1
            else:
                self.failed_parses += 1

        # Generate comprehensive report
        self.generate_report()

    def generate_report(self):
        """Generate comprehensive test report"""
        print(f"\n{'='*80}")
        print("📋 COMPREHENSIVE TEST REPORT")
        print(f"{'='*80}")

        successful_results = [r for r in self.results if r['status'] == 'success']
        failed_results = [r for r in self.results if r['status'] == 'failed']

        # Overall Statistics
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"  Total Files: {self.total_files}")
        print(f"  Successful Parses: {self.successful_parses} ({self.successful_parses/self.total_files*100:.1f}%)")
        print(f"  Failed Parses: {self.failed_parses} ({self.failed_parses/self.total_files*100:.1f}%)")

        if successful_results:
            avg_accuracy = sum(r['accuracy'] for r in successful_results) / len(successful_results)
            avg_parsing_time = sum(r['parsing_time'] for r in successful_results) / len(successful_results)
            brd_compliant = sum(1 for r in successful_results if r['brd_compliant'])
            performance_compliant = sum(1 for r in successful_results if r['performance_ok'])

            print(f"  Average Accuracy: {avg_accuracy:.1f}%")
            print(f"  Average Parsing Time: {avg_parsing_time*1000:.1f}ms")
            print(f"  BRD Compliant Files: {brd_compliant}/{len(successful_results)} ({brd_compliant/len(successful_results)*100:.1f}%)")
            print(f"  Performance Compliant: {performance_compliant}/{len(successful_results)} ({performance_compliant/len(successful_results)*100:.1f}%)")

        # Detailed Results
        print(f"\n📋 DETAILED RESULTS:")
        print(f"{'Rank':<4} {'File':<35} {'Status':<8} {'Accuracy':<9} {'Time':<8} {'BRD':<4} {'Issues':<6}")
        print("-" * 80)

        # Sort by accuracy (successful ones first, then failed)
        sorted_results = sorted(successful_results, key=lambda x: x['accuracy'], reverse=True) + failed_results

        for i, result in enumerate(sorted_results, 1):
            filename = result['filename'][:32] + "..." if len(result['filename']) > 35 else result['filename']

            if result['status'] == 'success':
                status = "✅ PASS" if result['accuracy'] >= 90 else "⚠️  WARN" if result['accuracy'] >= 80 else "❌ FAIL"
                accuracy = f"{result['accuracy']:.1f}%"
                time_str = f"{result['parsing_time']*1000:.1f}ms"
                brd_str = "✅" if result['brd_compliant'] else "❌"
                issues = str(len(result['issues']))
            else:
                status = "❌ ERROR"
                accuracy = "N/A"
                time_str = "N/A"
                brd_str = "❌"
                issues = "N/A"

            print(f"{i:<4} {filename:<35} {status:<8} {accuracy:<9} {time_str:<8} {brd_str:<4} {issues:<6}")

        # Critical Issues Summary
        print(f"\n🚨 CRITICAL ISSUES SUMMARY:")

        # Issue frequency analysis
        all_issues = []
        for result in successful_results:
            all_issues.extend(result.get('issues', []))

        # Count issue types
        issue_types = {}
        for issue in all_issues:
            # Extract issue type
            if 'position' in issue.lower():
                category = "Position Detection"
            elif 'name' in issue.lower():
                category = "Name Extraction"
            elif 'phone' in issue.lower() or 'email' in issue.lower():
                category = "Contact Information"
            elif 'skill' in issue.lower():
                category = "Skills Extraction"
            else:
                category = "Other"

            issue_types[category] = issue_types.get(category, 0) + 1

        print("Most Common Issue Categories:")
        for category, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True):
            percentage = count / len(successful_results) * 100 if successful_results else 0
            print(f"  • {category}: {count} occurrences ({percentage:.1f}% of files)")

        # Failed Files Analysis
        if failed_results:
            print(f"\n❌ FAILED FILES ANALYSIS:")
            for result in failed_results:
                print(f"  • {result['filename']}: {result.get('error', 'Unknown error')}")

        # Performance Analysis
        if successful_results:
            print(f"\n⏱️  PERFORMANCE ANALYSIS:")
            times = [r['parsing_time'] for r in successful_results]
            min_time = min(times) * 1000
            max_time = max(times) * 1000

            print(f"  Fastest Parse: {min_time:.1f}ms")
            print(f"  Slowest Parse: {max_time:.1f}ms")
            print(f"  Target Performance (<2ms): {sum(1 for t in times if t < 0.002)}/{len(times)} files")

        # Save detailed results to JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"rigorous_test_results_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump({
                'test_summary': {
                    'total_files': self.total_files,
                    'successful_parses': self.successful_parses,
                    'failed_parses': self.failed_parses,
                    'average_accuracy': avg_accuracy if successful_results else 0,
                    'average_parsing_time': avg_parsing_time if successful_results else 0,
                    'brd_compliant_count': brd_compliant if successful_results else 0,
                    'test_date': datetime.now().isoformat()
                },
                'detailed_results': self.results,
                'issue_analysis': issue_types
            }, f, indent=2)

        print(f"\n💾 Detailed results saved to: {output_file}")

        # Final Recommendations
        print(f"\n🎯 RECOMMENDATIONS:")
        if avg_accuracy < 85 if successful_results else True:
            print("  🚨 CRITICAL: Parser accuracy is below acceptable threshold")
            print("     → Immediate focus needed on position detection logic")
        elif avg_accuracy < 90 if successful_results else True:
            print("  ⚠️  WARNING: Parser accuracy needs improvement")
            print("     → Focus on contact information and skills extraction")
        else:
            print("  ✅ GOOD: Parser accuracy is meeting targets")

        if failed_results:
            print(f"  🔧 FIX: {len(failed_results)} files failing to parse")
            print("     → Address document format compatibility issues")

def main():
    """Main function to run the rigorous test suite"""
    suite = RigorousTestSuite()
    suite.run_comprehensive_test()

if __name__ == "__main__":
    main()