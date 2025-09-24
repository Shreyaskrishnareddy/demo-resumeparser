#!/usr/bin/env python3
"""
Comprehensive Parser Comparison Test
Compare optimized parser vs enterprise parser for accuracy validation
Ensures no functional compromise with speed optimization
"""

import json
import time
from datetime import datetime
from pathlib import Path

# Import both parsers
from enterprise_resume_parser import EnterpriseResumeParser
from optimized_parser import OptimizedResumeParser

class ParserComparison:
    def __init__(self):
        self.enterprise_parser = EnterpriseResumeParser()
        self.optimized_parser = OptimizedResumeParser()

    def load_test_resumes(self):
        """Load all available test resumes"""
        test_files = []

        # Load main test resume
        if Path('test_resume_sample.txt').exists():
            with open('test_resume_sample.txt', 'r') as f:
                test_files.append({
                    'name': 'test_resume_sample.txt',
                    'content': f.read(),
                    'expected': {
                        'name': 'John Smith',
                        'email': 'john.smith@email.com',
                        'company': 'TechCorp Inc',
                        'title': 'Senior Software Engineer',
                        'skills': ['Python', 'JavaScript', 'React', 'AWS', 'Docker']
                    }
                })

        # Add more comprehensive test cases
        test_files.extend([
            {
                'name': 'complex_resume_test',
                'content': """
Dr. Sarah Johnson, PhD
Principal Data Scientist & ML Engineer
sarah.johnson@techcorp.com | +1-555-987-6543 | San Francisco, CA

PROFESSIONAL SUMMARY
Data science leader with 12+ years experience in machine learning, statistical modeling, and big data analytics. Led teams of 15+ data scientists delivering $50M+ in business value through AI/ML solutions.

PROFESSIONAL EXPERIENCE

Principal Data Scientist | Google Inc | 2019 - Present
Led development of recommendation engine increasing user engagement by 35%
Managed cross-functional team of 15 engineers and data scientists
Technologies: Python, TensorFlow, BigQuery, Kubernetes, Apache Spark

Senior Data Scientist | Facebook Meta | 2016 - 2019
Built deep learning models for content ranking algorithms
Implemented A/B testing framework serving 2B+ users
Technologies: Python, PyTorch, Hadoop, Scala, SQL

EDUCATION
PhD in Statistics | Stanford University | 2014
MS in Computer Science | MIT | 2010

TECHNICAL SKILLS
Programming: Python, R, Scala, SQL, Java
ML/AI: TensorFlow, PyTorch, Scikit-learn, XGBoost, Keras
Big Data: Spark, Hadoop, Kafka, Flink, Airflow
Cloud: AWS, GCP, Azure, Kubernetes, Docker
""",
                'expected': {
                    'name': 'Dr. Sarah Johnson',
                    'email': 'sarah.johnson@techcorp.com',
                    'company': 'Google Inc',
                    'title': 'Principal Data Scientist',
                    'skills': ['Python', 'TensorFlow', 'ML', 'BigQuery', 'Kubernetes']
                }
            },
            {
                'name': 'entry_level_resume',
                'content': """
Mike Rodriguez
Junior Software Developer
mike.rodriguez@email.com | (555) 234-5678

OBJECTIVE
Recent computer science graduate seeking entry-level software development position to apply programming skills and contribute to innovative projects.

EDUCATION
Bachelor of Science in Computer Science
University of California, Davis | May 2023
GPA: 3.6/4.0
Relevant Coursework: Data Structures, Algorithms, Web Development, Database Systems

PROJECTS
Personal Portfolio Website | 2023
• Built responsive website using HTML, CSS, JavaScript, and React
• Implemented contact form with Node.js backend
• Deployed on AWS using S3 and CloudFront

Todo List Mobile App | 2023
• Developed cross-platform app using React Native
• Integrated with Firebase for real-time data synchronization
• Published on Google Play Store with 100+ downloads

TECHNICAL SKILLS
Programming Languages: JavaScript, Python, Java, HTML/CSS
Frameworks: React, Node.js, Express.js, React Native
Databases: MySQL, MongoDB, Firebase
Tools: Git, VS Code, Postman, AWS

EXPERIENCE
Software Development Intern | StartupXYZ | Summer 2022
• Assisted in developing web application features using React and Node.js
• Fixed bugs and improved application performance by 20%
• Participated in daily standups and sprint planning meetings
""",
                'expected': {
                    'name': 'Mike Rodriguez',
                    'email': 'mike.rodriguez@email.com',
                    'company': 'StartupXYZ',
                    'title': 'Software Development Intern',
                    'skills': ['JavaScript', 'Python', 'React', 'Node.js', 'AWS']
                }
            }
        ])

        return test_files

    def extract_fields_safely(self, result, parser_type):
        """Safely extract key fields from parser result"""
        extracted = {
            'name': '',
            'email': '',
            'phone': '',
            'company': '',
            'title': '',
            'skills': [],
            'experience_count': 0,
            'education_count': 0
        }

        try:
            # Contact Information
            contact = result.get('ContactInformation', {})

            # Name
            candidate_name = contact.get('CandidateName', {})
            extracted['name'] = candidate_name.get('FormattedName', '')

            # Email
            emails = contact.get('EmailAddresses', [])
            extracted['email'] = emails[0].get('EmailAddress', '') if emails else ''

            # Phone
            phones = contact.get('PhoneNumbers', [])
            extracted['phone'] = phones[0].get('PhoneNumber', '') if phones else ''

            # Work Experience
            experience = result.get('EmploymentHistory', {}).get('Positions', [])
            if not experience:
                experience = result.get('WorkExperience', [])

            extracted['experience_count'] = len(experience)

            if experience:
                current = experience[0]
                extracted['title'] = current.get('JobTitle', '')

                # Company extraction
                employer = current.get('Employer', {})
                if isinstance(employer, dict):
                    extracted['company'] = employer.get('Name', '')
                else:
                    extracted['company'] = current.get('EmployerName', '')

            # Skills
            skills = result.get('Skills', [])
            skill_names = []
            for skill in skills:
                if isinstance(skill, dict):
                    skill_name = skill.get('Name', '') or skill.get('SkillName', '')
                    if skill_name:
                        skill_names.append(skill_name)
                elif isinstance(skill, str):
                    skill_names.append(skill)

            extracted['skills'] = skill_names[:20]  # Limit for comparison

            # Education
            education = result.get('Education', {})
            if isinstance(education, dict):
                extracted['education_count'] = len(education.get('EducationDetails', []))
            else:
                extracted['education_count'] = len(education) if isinstance(education, list) else 0

        except Exception as e:
            print(f"Error extracting from {parser_type}: {e}")

        return extracted

    def calculate_field_accuracy(self, expected, extracted):
        """Calculate accuracy for individual fields"""
        scores = {}

        # Name accuracy
        scores['name'] = 100 if expected['name'].lower() in extracted['name'].lower() else 0

        # Email accuracy
        scores['email'] = 100 if expected['email'].lower() == extracted['email'].lower() else 0

        # Company accuracy
        scores['company'] = 100 if expected['company'].lower() in extracted['company'].lower() else 0

        # Title accuracy
        scores['title'] = 100 if expected['title'].lower() in extracted['title'].lower() else 0

        # Skills accuracy
        found_skills = 0
        for expected_skill in expected['skills']:
            for extracted_skill in extracted['skills']:
                if expected_skill.lower() in extracted_skill.lower():
                    found_skills += 1
                    break

        scores['skills'] = (found_skills / len(expected['skills'])) * 100 if expected['skills'] else 0

        return scores

    def compare_parsers(self, test_files):
        """Compare both parsers across all test files"""
        results = []

        print("🔍 COMPREHENSIVE PARSER COMPARISON")
        print("=" * 80)

        for i, test_file in enumerate(test_files, 1):
            print(f"\n📄 Test {i}: {test_file['name']}")
            print("-" * 50)

            # Parse with Enterprise Parser
            print("Testing Enterprise Parser...")
            start_time = time.perf_counter()
            try:
                enterprise_result = self.enterprise_parser.parse_resume(test_file['content'])
                enterprise_time = (time.perf_counter() - start_time) * 1000
                enterprise_success = True
            except Exception as e:
                print(f"❌ Enterprise parser failed: {e}")
                enterprise_result = {}
                enterprise_time = 0
                enterprise_success = False

            # Parse with Optimized Parser
            print("Testing Optimized Parser...")
            start_time = time.perf_counter()
            try:
                optimized_result = self.optimized_parser.parse_resume_fast(test_file['content'])
                optimized_time = (time.perf_counter() - start_time) * 1000
                optimized_success = True
            except Exception as e:
                print(f"❌ Optimized parser failed: {e}")
                optimized_result = {}
                optimized_time = 0
                optimized_success = False

            # Extract and compare results
            if enterprise_success and optimized_success:
                enterprise_extracted = self.extract_fields_safely(enterprise_result, "Enterprise")
                optimized_extracted = self.extract_fields_safely(optimized_result, "Optimized")

                enterprise_scores = self.calculate_field_accuracy(test_file['expected'], enterprise_extracted)
                optimized_scores = self.calculate_field_accuracy(test_file['expected'], optimized_extracted)

                # Display comparison
                print("\n📊 ACCURACY COMPARISON:")
                print("-" * 30)

                fields = ['name', 'email', 'company', 'title', 'skills']
                for field in fields:
                    ent_score = enterprise_scores.get(field, 0)
                    opt_score = optimized_scores.get(field, 0)

                    status = "✅" if abs(ent_score - opt_score) <= 10 else "⚠️"
                    print(f"{status} {field.title()}: Enterprise {ent_score:.1f}% | Optimized {opt_score:.1f}%")

                # Performance comparison
                print(f"\n⚡ PERFORMANCE:")
                print(f"   Enterprise: {enterprise_time:.2f}ms")
                print(f"   Optimized:  {optimized_time:.2f}ms")
                print(f"   Speedup:    {enterprise_time/optimized_time:.1f}x faster")

                # Overall scores
                ent_overall = sum(enterprise_scores.values()) / len(enterprise_scores)
                opt_overall = sum(optimized_scores.values()) / len(optimized_scores)

                print(f"\n📈 OVERALL ACCURACY:")
                print(f"   Enterprise: {ent_overall:.1f}%")
                print(f"   Optimized:  {opt_overall:.1f}%")
                print(f"   Difference: {abs(ent_overall - opt_overall):.1f}%")

                # Store results
                test_result = {
                    'test_name': test_file['name'],
                    'enterprise': {
                        'success': enterprise_success,
                        'time_ms': enterprise_time,
                        'extracted': enterprise_extracted,
                        'scores': enterprise_scores,
                        'overall_accuracy': ent_overall
                    },
                    'optimized': {
                        'success': optimized_success,
                        'time_ms': optimized_time,
                        'extracted': optimized_extracted,
                        'scores': optimized_scores,
                        'overall_accuracy': opt_overall
                    },
                    'expected': test_file['expected'],
                    'speedup': enterprise_time/optimized_time if optimized_time > 0 else 0,
                    'accuracy_loss': ent_overall - opt_overall
                }

                results.append(test_result)

            print()

        return results

    def generate_comprehensive_report(self, results):
        """Generate comprehensive comparison report"""
        print("\n" + "=" * 80)
        print("📋 COMPREHENSIVE COMPARISON REPORT")
        print("=" * 80)

        if not results:
            print("❌ No successful test results to analyze")
            return

        # Calculate aggregate statistics
        total_tests = len(results)
        avg_enterprise_accuracy = sum(r['enterprise']['overall_accuracy'] for r in results) / total_tests
        avg_optimized_accuracy = sum(r['optimized']['overall_accuracy'] for r in results) / total_tests
        avg_speedup = sum(r['speedup'] for r in results) / total_tests
        avg_accuracy_loss = sum(abs(r['accuracy_loss']) for r in results) / total_tests

        print(f"\n📊 AGGREGATE STATISTICS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Enterprise Parser Avg Accuracy: {avg_enterprise_accuracy:.1f}%")
        print(f"   Optimized Parser Avg Accuracy: {avg_optimized_accuracy:.1f}%")
        print(f"   Average Speedup: {avg_speedup:.1f}x")
        print(f"   Average Accuracy Loss: {avg_accuracy_loss:.1f}%")

        # Quality assessment
        print(f"\n🎯 QUALITY ASSESSMENT:")
        acceptable_loss = avg_accuracy_loss <= 5  # Max 5% accuracy loss acceptable
        good_speedup = avg_speedup >= 10  # At least 10x speedup

        print(f"   Accuracy Loss Acceptable: {'✅ YES' if acceptable_loss else '❌ NO'} ({avg_accuracy_loss:.1f}% <= 5%)")
        print(f"   Speedup Satisfactory: {'✅ YES' if good_speedup else '❌ NO'} ({avg_speedup:.1f}x >= 10x)")

        # Overall recommendation
        if acceptable_loss and good_speedup:
            print(f"\n🎉 RECOMMENDATION: ✅ OPTIMIZED PARSER APPROVED")
            print("   The optimized parser maintains accuracy while delivering excellent performance.")
        elif acceptable_loss:
            print(f"\n⚠️ RECOMMENDATION: 🔄 SPEED OPTIMIZATION NEEDED")
            print("   Accuracy is maintained but speedup is insufficient.")
        else:
            print(f"\n❌ RECOMMENDATION: 🛠️ ACCURACY IMPROVEMENTS NEEDED")
            print("   Significant accuracy loss detected. Optimized parser needs refinement.")

        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report = {
            'timestamp': timestamp,
            'summary': {
                'total_tests': total_tests,
                'avg_enterprise_accuracy': avg_enterprise_accuracy,
                'avg_optimized_accuracy': avg_optimized_accuracy,
                'avg_speedup': avg_speedup,
                'avg_accuracy_loss': avg_accuracy_loss,
                'acceptable_loss': acceptable_loss,
                'good_speedup': good_speedup
            },
            'detailed_results': results
        }

        report_file = f"parser_comparison_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\nDetailed report saved: {report_file}")

        return report

def main():
    """Main comparison function"""
    comparison = ParserComparison()

    # Load test resumes
    test_files = comparison.load_test_resumes()
    print(f"Loaded {len(test_files)} test resumes for comparison")

    # Run comparison
    results = comparison.compare_parsers(test_files)

    # Generate report
    if results:
        comparison.generate_comprehensive_report(results)
    else:
        print("❌ No results to analyze - check parser implementations")

if __name__ == "__main__":
    main()