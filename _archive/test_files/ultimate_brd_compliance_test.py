#!/usr/bin/env python3
"""
Ultimate BRD Compliance Test Suite
Validates 100% BRD compliance against real resume data
"""

import time
import json
from pathlib import Path
from lightning_fast_parser import LightningFastParser
from robust_document_extractor import extract_text_robust

class UltimateBRDComplianceTest:
    """
    Comprehensive BRD compliance validation
    """

    def __init__(self):
        self.parser = LightningFastParser()
        self.brd_requirements = {
            'max_processing_time_ms': 2.0,
            'min_accuracy_percentage': 90.0,
            'required_fields': ['name', 'email', 'positions']
        }

    def run_comprehensive_test(self, test_dir: str) -> dict:
        """Run complete BRD compliance test suite"""
        print("🎯 ULTIMATE BRD COMPLIANCE TEST")
        print("=" * 60)

        test_results = {
            'total_files': 0,
            'successful_parses': 0,
            'brd_compliant_files': 0,
            'performance_compliant': 0,
            'accuracy_compliant': 0,
            'avg_processing_time': 0,
            'file_results': [],
            'performance_stats': {
                'fastest_ms': float('inf'),
                'slowest_ms': 0,
                'sub_1ms_count': 0,
                'sub_2ms_count': 0
            }
        }

        # Get test files
        test_path = Path(test_dir)
        resume_files = [
            f for f in test_path.glob('*')
            if f.suffix.lower() in ['.pdf', '.doc', '.docx']
            and not f.name.endswith('.Zone.Identifier')
        ]

        test_results['total_files'] = len(resume_files)
        print(f"📁 Testing {len(resume_files)} resume files\n")

        processing_times = []

        for i, file_path in enumerate(resume_files, 1):
            print(f"🧪 TEST {i}/{len(resume_files)}: {file_path.name}")
            print("-" * 50)

            # Extract text
            start_extraction = time.perf_counter()
            text, extraction_method = extract_text_robust(str(file_path))
            extraction_time = (time.perf_counter() - start_extraction) * 1000

            if text.startswith('Error:'):
                print(f"❌ Text extraction failed: {text}")
                continue

            print(f"✅ Text extracted ({len(text)} chars) via {extraction_method}")

            # Parse resume
            try:
                result = self.parser.parse_resume(text, file_path.name)
                processing_time = result['ParsingMetadata']['ProcessingTimeMs']
                processing_times.append(processing_time)

                # Evaluate BRD compliance
                compliance_result = self._evaluate_brd_compliance(result, file_path.name)

                # Update statistics
                test_results['successful_parses'] += 1

                if compliance_result['brd_compliant']:
                    test_results['brd_compliant_files'] += 1

                if processing_time < 2.0:
                    test_results['performance_compliant'] += 1

                if processing_time < 1.0:
                    test_results['performance_stats']['sub_1ms_count'] += 1

                if processing_time < 2.0:
                    test_results['performance_stats']['sub_2ms_count'] += 1

                # Update performance stats
                perf_stats = test_results['performance_stats']
                perf_stats['fastest_ms'] = min(perf_stats['fastest_ms'], processing_time)
                perf_stats['slowest_ms'] = max(perf_stats['slowest_ms'], processing_time)

                # Store detailed results
                test_results['file_results'].append({
                    'filename': file_path.name,
                    'processing_time_ms': processing_time,
                    'extraction_time_ms': round(extraction_time, 3),
                    'positions_found': result['ParsingMetadata']['PositionsFound'],
                    'has_name': bool(result['PersonName']['GivenName']),
                    'has_email': bool(result['ContactMethod'][0].get('InternetEmailAddress') if result['ContactMethod'] else False),
                    'has_phone': bool(result['Telephones']),
                    'brd_compliant': compliance_result['brd_compliant'],
                    'accuracy_score': compliance_result['accuracy_score'],
                    'issues': compliance_result['issues']
                })

                # Display results
                print(f"⏱️  Processing: {processing_time:.3f}ms")
                print(f"🎯 BRD Compliant: {'✅' if compliance_result['brd_compliant'] else '❌'}")
                print(f"📈 Accuracy: {compliance_result['accuracy_score']:.1f}%")

                if compliance_result['issues']:
                    print(f"⚠️  Issues: {', '.join(compliance_result['issues'])}")

                print()

            except Exception as e:
                print(f"❌ Parsing failed: {str(e)}\n")
                continue

        # Calculate final statistics
        if processing_times:
            test_results['avg_processing_time'] = sum(processing_times) / len(processing_times)

        # Generate summary
        self._generate_summary(test_results)

        return test_results

    def _evaluate_brd_compliance(self, result: dict, filename: str) -> dict:
        """Evaluate BRD compliance for a single result"""
        issues = []
        accuracy_factors = []

        # Check processing time
        processing_time = result['ParsingMetadata']['ProcessingTimeMs']
        if processing_time >= 2.0:
            issues.append(f"Processing time {processing_time:.2f}ms exceeds 2ms limit")
        else:
            accuracy_factors.append(1.0)

        # Check name extraction
        has_name = bool(result['PersonName']['GivenName'])
        if not has_name:
            issues.append("No name found")
        else:
            accuracy_factors.append(1.0)

        # Check email extraction
        has_email = bool(result['ContactMethod'][0].get('InternetEmailAddress') if result['ContactMethod'] else False)
        if not has_email:
            issues.append("No email found")
        else:
            accuracy_factors.append(1.0)

        # Check position extraction
        positions_count = result['ParsingMetadata']['PositionsFound']
        if positions_count == 0:
            issues.append("No positions found")
        elif positions_count > 10:
            issues.append(f"Too many positions ({positions_count}) - possible over-detection")
            accuracy_factors.append(0.5)  # Partial credit
        else:
            accuracy_factors.append(1.0)

        # Calculate accuracy score
        accuracy_score = (sum(accuracy_factors) / 4.0) * 100 if accuracy_factors else 0

        # BRD compliant if no issues and high accuracy
        brd_compliant = len(issues) == 0 and accuracy_score >= 90.0

        return {
            'brd_compliant': brd_compliant,
            'accuracy_score': accuracy_score,
            'issues': issues
        }

    def _generate_summary(self, results: dict):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🏆 ULTIMATE BRD COMPLIANCE TEST RESULTS")
        print("=" * 60)

        total = results['total_files']
        successful = results['successful_parses']
        compliant = results['brd_compliant_files']

        print(f"\n📊 OVERALL STATISTICS:")
        print(f"  Total Files: {total}")
        print(f"  Successful Parses: {successful}/{total} ({successful/total*100:.1f}%)")
        print(f"  BRD Compliant: {compliant}/{successful} ({compliant/successful*100 if successful else 0:.1f}%)")
        print(f"  Performance Compliant (<2ms): {results['performance_compliant']}/{successful}")

        if results['avg_processing_time']:
            print(f"\n⏱️  PERFORMANCE ANALYSIS:")
            avg_time = results['avg_processing_time']
            perf = results['performance_stats']
            print(f"  Average Processing Time: {avg_time:.3f}ms")
            print(f"  Fastest: {perf['fastest_ms']:.3f}ms")
            print(f"  Slowest: {perf['slowest_ms']:.3f}ms")
            print(f"  Sub-1ms Count: {perf['sub_1ms_count']}")
            print(f"  Sub-2ms Count: {perf['sub_2ms_count']}")

        print(f"\n🎯 BRD COMPLIANCE ASSESSMENT:")
        if compliant == successful and successful > 0:
            print("  🟢 PERFECT: 100% BRD COMPLIANCE ACHIEVED!")
        elif compliant >= successful * 0.9:
            print("  🟡 EXCELLENT: 90%+ BRD compliance achieved")
        elif compliant >= successful * 0.7:
            print("  🟠 GOOD: 70%+ BRD compliance achieved")
        else:
            print("  🔴 NEEDS IMPROVEMENT: <70% BRD compliance")

        # Top performers
        if results['file_results']:
            compliant_files = [f for f in results['file_results'] if f['brd_compliant']]
            if compliant_files:
                print(f"\n🏅 TOP BRD-COMPLIANT FILES:")
                for i, file_result in enumerate(sorted(compliant_files, key=lambda x: x['processing_time_ms'])[:5], 1):
                    print(f"  {i}. {file_result['filename']}: {file_result['processing_time_ms']:.3f}ms")

        print(f"\n{'=' * 60}")


if __name__ == "__main__":
    tester = UltimateBRDComplianceTest()

    # Run comprehensive test
    test_dir = "/home/great/claudeprojects/parser/test_resumes/Test Resumes"
    results = tester.run_comprehensive_test(test_dir)

    # Save results
    with open('ultimate_brd_compliance_results.json', 'w') as f:
        json.dump(results, f, indent=2)