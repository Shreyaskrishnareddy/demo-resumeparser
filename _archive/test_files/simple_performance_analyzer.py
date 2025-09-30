#!/usr/bin/env python3
"""
Simple Performance Analyzer for Resume Parser
Identifies bottlenecks without external dependencies
"""

import time
import re
import json
from datetime import datetime
from typing import Dict, List, Any


class SimplePerformanceAnalyzer:
    """Analyze parser performance without external dependencies"""

    def __init__(self):
        self.sample_resume = """
John Smith
Senior Software Engineer
Email: john.smith@email.com | Phone: (555) 123-4567

PROFESSIONAL SUMMARY
Experienced software engineer with 8+ years in full-stack development, cloud architecture, and team leadership.
Proven track record of delivering scalable solutions and mentoring development teams.

PROFESSIONAL EXPERIENCE
Senior Software Engineer
TechCorp Inc - San Francisco, CA
January 2020 - Current
• Lead development of microservices architecture serving 1M+ users
• Implemented CI/CD pipelines reducing deployment time by 60%
• Mentor team of 5 junior developers
• Technologies: Python, React, AWS, Docker, Kubernetes

Software Developer
StartupXYZ - Austin, TX
June 2018 - December 2019
• Built REST APIs using Python Flask and PostgreSQL
• Collaborated with product team on feature development
• Maintained CI/CD pipelines using Jenkins

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley
2014 - 2018

TECHNICAL SKILLS
Programming Languages: Python, JavaScript, Java, C++
Web Technologies: React, Angular, Node.js, HTML/CSS
Databases: PostgreSQL, MongoDB, Redis, MySQL
Cloud & DevOps: AWS, Docker, Kubernetes, Jenkins, Git
Other: Microservices, REST APIs, Agile/Scrum, Unit Testing

PROJECTS
E-commerce Platform
• Built full-stack application with React frontend and Node.js backend
• Integrated payment processing and inventory management
• Deployed on AWS with auto-scaling capabilities

CERTIFICATIONS
AWS Certified Solutions Architect - 2021
Certified Scrum Master - 2020

LANGUAGES
English (Native)
Spanish (Conversational)
"""

    def time_operation(self, operation_name: str, operation_func, *args, **kwargs) -> float:
        """Time a single operation"""
        start_time = time.perf_counter()
        try:
            result = operation_func(*args, **kwargs)
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            print(f"  {operation_name}: {duration_ms:.3f}ms")
            return duration_ms
        except Exception as e:
            print(f"  {operation_name}: ERROR - {e}")
            return 0.0

    def analyze_text_operations(self, text: str) -> Dict[str, float]:
        """Analyze basic text processing operations"""
        print("📝 Analyzing text processing operations...")

        operations = {}

        # String operations
        operations['split_lines'] = self.time_operation(
            "split_lines", lambda: text.split('\n')
        )

        operations['lowercase'] = self.time_operation(
            "lowercase", lambda: text.lower()
        )

        operations['strip_lines'] = self.time_operation(
            "strip_lines", lambda: [line.strip() for line in text.split('\n')]
        )

        # Regex operations
        email_pattern = re.compile(r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b')
        operations['find_emails'] = self.time_operation(
            "find_emails", lambda: email_pattern.findall(text)
        )

        phone_pattern = re.compile(r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})')
        operations['find_phones'] = self.time_operation(
            "find_phones", lambda: phone_pattern.findall(text)
        )

        # Complex processing
        operations['extract_sections'] = self.time_operation(
            "extract_sections", self._extract_sections, text
        )

        operations['extract_work_experience'] = self.time_operation(
            "extract_work_experience", self._extract_work_experience_simple, text
        )

        return operations

    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Simple section extraction"""
        sections = {}
        lines = text.split('\n')
        current_section = None
        current_content = []

        section_headers = ['SUMMARY', 'EXPERIENCE', 'EDUCATION', 'SKILLS', 'PROJECTS', 'CERTIFICATIONS']

        for line in lines:
            line = line.strip()
            if any(header in line.upper() for header in section_headers):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.upper()
                current_content = []
            elif current_section:
                current_content.append(line)

        if current_section:
            sections[current_section] = '\n'.join(current_content)

        return sections

    def _extract_work_experience_simple(self, text: str) -> List[Dict[str, str]]:
        """Simple work experience extraction"""
        experiences = []
        lines = text.split('\n')

        # Look for job patterns
        for i, line in enumerate(lines):
            line = line.strip()
            if any(title in line for title in ['Engineer', 'Developer', 'Manager', 'Analyst']):
                # Found potential job title
                experience = {'title': line}

                # Look for company in next few lines
                for j in range(i+1, min(i+3, len(lines))):
                    next_line = lines[j].strip()
                    if any(indicator in next_line for indicator in ['Inc', 'Corp', 'LLC', 'Company']):
                        experience['company'] = next_line
                        break

                experiences.append(experience)

        return experiences

    def analyze_brd_operations(self) -> Dict[str, float]:
        """Analyze BRD-specific operations"""
        print("\n⚙️ Analyzing BRD transformation operations...")

        text = self.sample_resume
        operations = {}

        # Simulate BRD transformations
        operations['name_extraction'] = self.time_operation(
            "name_extraction", self._extract_name, text
        )

        operations['skill_synonyms'] = self.time_operation(
            "skill_synonyms", self._find_skill_synonyms, "Python"
        )

        operations['date_parsing'] = self.time_operation(
            "date_parsing", self._parse_dates, text
        )

        operations['education_extraction'] = self.time_operation(
            "education_extraction", self._extract_education, text
        )

        return operations

    def _extract_name(self, text: str) -> str:
        """Extract candidate name"""
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and not any(keyword in line.lower() for keyword in ['email', 'phone', 'engineer']):
                words = line.split()
                if 2 <= len(words) <= 4 and all(word.replace('.', '').isalpha() for word in words):
                    return line
        return ""

    def _find_skill_synonyms(self, skill: str) -> List[str]:
        """Find skill synonyms"""
        synonyms_db = {
            'python': ['python', 'python3', 'py'],
            'javascript': ['javascript', 'js', 'ecmascript'],
            'react': ['react', 'reactjs', 'react.js']
        }
        return synonyms_db.get(skill.lower(), [skill])

    def _parse_dates(self, text: str) -> List[str]:
        """Parse dates from text"""
        date_pattern = re.compile(r'(20\d{2})')
        return date_pattern.findall(text)

    def _extract_education(self, text: str) -> List[str]:
        """Extract education information"""
        education = []
        lines = text.split('\n')

        for line in lines:
            if any(degree in line.lower() for degree in ['bachelor', 'master', 'phd', 'diploma']):
                education.append(line.strip())

        return education

    def measure_full_parsing(self, iterations: int = 10) -> Dict[str, Any]:
        """Measure complete parsing performance"""
        print(f"\n⏱️ Measuring full parsing performance ({iterations} iterations)...")

        times = []
        for i in range(iterations):
            start_time = time.perf_counter()

            # Simulate complete parsing pipeline
            sections = self._extract_sections(self.sample_resume)
            name = self._extract_name(self.sample_resume)
            experience = self._extract_work_experience_simple(self.sample_resume)
            education = self._extract_education(self.sample_resume)
            dates = self._parse_dates(self.sample_resume)

            end_time = time.perf_counter()
            parse_time = (end_time - start_time) * 1000
            times.append(parse_time)

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Min: {min_time:.2f}ms")
        print(f"  Max: {max_time:.2f}ms")
        print(f"  Target: 2.00ms")
        print(f"  Gap: {avg_time - 2:.2f}ms")
        print(f"  Speedup needed: {avg_time / 2:.1f}x")

        return {
            'average_ms': avg_time,
            'min_ms': min_time,
            'max_ms': max_time,
            'target_ms': 2.0,
            'gap_ms': avg_time - 2.0,
            'speedup_needed': avg_time / 2.0,
            'all_times': times
        }

    def analyze_current_parser(self) -> Dict[str, Any]:
        """Analyze the actual parser files"""
        print("\n🔍 Analyzing current parser implementation...")

        # Read and analyze brd_transformer.py
        try:
            with open('/home/great/claudeprojects/parser/parserdemo/brd_transformer.py', 'r') as f:
                brd_content = f.read()

            analysis = {
                'file_size_kb': len(brd_content) / 1024,
                'line_count': len(brd_content.split('\n')),
                'import_count': len([line for line in brd_content.split('\n') if line.strip().startswith('import') or line.strip().startswith('from')]),
                'function_count': len([line for line in brd_content.split('\n') if line.strip().startswith('def ')]),
                'regex_patterns': len(re.findall(r're\.compile|re\.search|re\.findall', brd_content)),
                'loops': len(re.findall(r'for .+ in |while ', brd_content)),
                'complex_operations': []
            }

            # Identify potentially expensive operations
            expensive_ops = [
                ('split operations', len(re.findall(r'\.split\(', brd_content))),
                ('string replacements', len(re.findall(r'\.replace\(', brd_content))),
                ('regex searches', len(re.findall(r'\.search\(|\.findall\(', brd_content))),
                ('list comprehensions', len(re.findall(r'\[.+ for .+ in .+\]', brd_content))),
                ('dictionary operations', len(re.findall(r'\.get\(|\.items\(\)|\.values\(\)', brd_content)))
            ]

            analysis['expensive_operations'] = expensive_ops

            print(f"  File size: {analysis['file_size_kb']:.1f}KB")
            print(f"  Lines of code: {analysis['line_count']}")
            print(f"  Import statements: {analysis['import_count']}")
            print(f"  Functions: {analysis['function_count']}")
            print(f"  Regex patterns: {analysis['regex_patterns']}")
            print(f"  Loops: {analysis['loops']}")

            print("\n  Potentially expensive operations:")
            for op_name, count in expensive_ops:
                if count > 0:
                    print(f"    {op_name}: {count}")

            return analysis

        except Exception as e:
            print(f"  Error analyzing parser files: {e}")
            return {}

    def generate_optimization_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate specific optimization recommendations"""
        recommendations = []

        parsing_time = analysis_results.get('full_parsing', {}).get('average_ms', 0)

        if parsing_time > 10:
            recommendations.append("🚨 HIGH PRIORITY: Parsing time is extremely slow - focus on algorithmic improvements")

        if parsing_time > 5:
            recommendations.append("⚡ Pre-compile all regex patterns at module initialization")
            recommendations.append("🗄️ Cache frequently accessed data structures")

        text_ops = analysis_results.get('text_operations', {})
        if text_ops.get('extract_work_experience', 0) > 2:
            recommendations.append("🔧 Optimize work experience extraction - major bottleneck")

        if text_ops.get('find_emails', 0) > 0.5:
            recommendations.append("📧 Consider simpler email extraction method")

        parser_analysis = analysis_results.get('parser_analysis', {})
        if parser_analysis.get('regex_patterns', 0) > 10:
            recommendations.append("🔍 Too many regex patterns - consider consolidation")

        if parser_analysis.get('loops', 0) > 20:
            recommendations.append("🔄 High loop count - look for vectorization opportunities")

        # General optimizations
        recommendations.extend([
            "💾 Implement lazy loading for heavy imports",
            "🏃‍♂️ Use string operations instead of regex where possible",
            "🎯 Reduce scope of text processing to essential fields only",
            "⚡ Consider parallel processing for independent operations",
            "🗜️ Minimize object creation in hot paths"
        ])

        return recommendations

    def run_complete_analysis(self) -> Dict[str, Any]:
        """Run complete performance analysis"""
        print("🎯 RESUME PARSER PERFORMANCE ANALYSIS")
        print("=" * 60)

        results = {}

        # 1. Analyze text operations
        results['text_operations'] = self.analyze_text_operations(self.sample_resume)

        # 2. Analyze BRD operations
        results['brd_operations'] = self.analyze_brd_operations()

        # 3. Measure full parsing
        results['full_parsing'] = self.measure_full_parsing()

        # 4. Analyze parser implementation
        results['parser_analysis'] = self.analyze_current_parser()

        # 5. Generate recommendations
        recommendations = self.generate_optimization_recommendations(results)

        # Print summary
        print(f"\n📊 PERFORMANCE SUMMARY:")
        print(f"Current parsing time: {results['full_parsing']['average_ms']:.2f}ms")
        print(f"Target time: 2.00ms")
        print(f"Improvement needed: {results['full_parsing']['speedup_needed']:.1f}x faster")

        print(f"\n💡 OPTIMIZATION RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i:2d}. {rec}")

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"/home/great/claudeprojects/parser/parserdemo/simple_performance_analysis_{timestamp}.json"

        json_data = {
            'timestamp': datetime.now().isoformat(),
            'analysis_results': {
                'text_operations': results['text_operations'],
                'brd_operations': results['brd_operations'],
                'full_parsing': {
                    'average_ms': results['full_parsing']['average_ms'],
                    'min_ms': results['full_parsing']['min_ms'],
                    'max_ms': results['full_parsing']['max_ms'],
                    'gap_ms': results['full_parsing']['gap_ms'],
                    'speedup_needed': results['full_parsing']['speedup_needed']
                },
                'parser_analysis': results['parser_analysis']
            },
            'recommendations': recommendations
        }

        with open(results_file, 'w') as f:
            json.dump(json_data, f, indent=2)

        print(f"\n📁 Results saved to: {results_file}")

        return results


def main():
    analyzer = SimplePerformanceAnalyzer()
    results = analyzer.run_complete_analysis()
    return results


if __name__ == "__main__":
    main()