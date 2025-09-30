#!/usr/bin/env python3
"""
Targeted Test: Position Over-Detection Issue
Tests the most critical issue affecting 4/5 failing cases
"""

from fixed_resume_parser import FixedResumeParser
import fitz
import docx
from pathlib import Path

def extract_text_from_file(file_path, filename):
    """Extract text from file"""
    try:
        file_ext = Path(filename).suffix.lower()
        if file_ext == '.pdf':
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        elif file_ext in ['.docx', '.doc']:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
    except Exception as e:
        return f"Error: {str(e)}"

def test_position_detection_case(filename, expected_positions, expected_companies):
    """Test position detection for a specific case"""
    file_path = f"/home/great/claudeprojects/parser/test_resumes/Test Resumes/{filename}"

    print(f"\n🧪 Testing: {filename}")
    print(f"Expected Positions: {expected_positions}")
    print(f"Expected Companies: {expected_companies}")
    print("-" * 50)

    # Extract and parse
    text = extract_text_from_file(file_path, filename)
    if text.startswith('Error'):
        print(f"❌ Text extraction failed: {text}")
        return

    parser = FixedResumeParser()
    result = parser.parse_resume(text, filename)

    positions = result.get('EmploymentHistory', {}).get('Positions', [])
    found_positions = len(positions)

    print(f"📊 Results:")
    print(f"  Positions Found: {found_positions} (Expected: {expected_positions})")

    # Show all positions found
    print(f"\n💼 All Positions Detected:")
    for i, pos in enumerate(positions, 1):
        company = pos.get('Employer', {}).get('Name', 'Unknown')
        title = pos.get('JobTitle', 'Unknown')
        dates = pos.get('Dates', 'Unknown')

        # Determine if this looks like a valid position or job duty
        is_valid = "✅" if any(expected_company.lower() in company.lower() for expected_company in expected_companies) else "❓"
        if len(company) < 5 or company.lower().startswith(('implement', 'develop', 'manage', 'perform', 'establish', 'architect', 'client:')):
            is_valid = "❌"

        print(f"  {i:2}. {is_valid} {company} | {title} | {dates}")

    # Analysis
    accuracy = (min(found_positions, expected_positions) / max(found_positions, expected_positions)) * 100
    print(f"\n📈 Analysis:")
    print(f"  Position Count Accuracy: {accuracy:.1f}%")

    if found_positions > expected_positions * 2:
        print(f"  🚨 CRITICAL: Over-detection by {found_positions - expected_positions} positions")
    elif found_positions > expected_positions:
        print(f"  ⚠️  WARNING: Over-detection by {found_positions - expected_positions} positions")
    elif found_positions < expected_positions:
        print(f"  ⚠️  WARNING: Under-detection by {expected_positions - found_positions} positions")
    else:
        print(f"  ✅ GOOD: Position count matches expectation")

    return {
        'filename': filename,
        'expected': expected_positions,
        'found': found_positions,
        'accuracy': accuracy,
        'status': 'PASS' if abs(found_positions - expected_positions) <= 1 else 'FAIL'
    }

def main():
    """Main testing function"""
    print("🎯 TARGETED TEST: Position Over-Detection Issue")
    print("=" * 60)

    # Test cases based on analysis
    test_cases = [
        {
            'filename': 'Dexter Nigel Ramkissoon.docx',
            'expected_positions': 4,
            'expected_companies': ['Trinitek', 'Previous Company', 'Another Company', 'Early Career']
        },
        {
            'filename': 'Donald Belvin.docx',
            'expected_positions': 5,
            'expected_companies': ['Genesis 10', 'Bank of America', 'Previous Role', 'Early Career', 'First Job']
        },
        {
            'filename': 'Mutchie.docx',
            'expected_positions': 4,
            'expected_companies': ['BRIGHT COMPUTING', 'GOVCONNECTION', 'Previous Role', 'Early Career']
        },
        {
            'filename': 'PRANAY REDDY_DE_Resume.pdf',
            'expected_positions': 4,
            'expected_companies': ['Current Company', 'Previous Company', 'Earlier Role', 'First Job']
        }
    ]

    results = []
    for test_case in test_cases:
        try:
            result = test_position_detection_case(
                test_case['filename'],
                test_case['expected_positions'],
                test_case['expected_companies']
            )
            if result:
                results.append(result)
        except Exception as e:
            print(f"❌ Error testing {test_case['filename']}: {str(e)}")

    # Summary
    print(f"\n{'='*60}")
    print("📋 POSITION OVER-DETECTION TEST SUMMARY")
    print(f"{'='*60}")

    passed = sum(1 for r in results if r['status'] == 'PASS')
    total = len(results)
    avg_accuracy = sum(r['accuracy'] for r in results) / len(results) if results else 0

    print(f"Tests Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"Average Position Count Accuracy: {avg_accuracy:.1f}%")

    print(f"\n🎯 Individual Results:")
    for result in results:
        status_icon = "✅" if result['status'] == 'PASS' else "❌"
        print(f"  {status_icon} {result['filename']}: {result['found']} found (expected {result['expected']}) - {result['accuracy']:.1f}%")

    if avg_accuracy < 70:
        print(f"\n🚨 CRITICAL: Position over-detection is a major issue requiring immediate fix")
    elif avg_accuracy < 85:
        print(f"\n⚠️  WARNING: Position detection needs improvement")
    else:
        print(f"\n✅ GOOD: Position detection is performing well")

if __name__ == "__main__":
    main()