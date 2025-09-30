#!/usr/bin/env python3
"""
Detailed analysis of failing resume parsing cases
"""

from fixed_resume_parser import FixedResumeParser
import fitz
import docx
from pathlib import Path
import json

# List of problematic files identified from tests
FAILING_CASES = [
    {
        'file': 'Ashok Kumar.doc',
        'accuracy': '88%',
        'issues': ['Name extraction: "file formats like"', 'Contact info issues']
    },
    {
        'file': 'Dexter Nigel Ramkissoon.docx',
        'accuracy': '76%',
        'issues': ['Low skill count (6)', 'High experience count mismatch']
    },
    {
        'file': 'Donald Belvin.docx',
        'accuracy': '80%',
        'issues': ['Only 1 experience found', 'Experience detection failure']
    },
    {
        'file': 'Mutchie.docx',
        'accuracy': '84%',
        'issues': ['Name formatting issues', 'Experience parsing']
    },
    {
        'file': 'PRANAY REDDY_DE_Resume.pdf',
        'accuracy': '84%',
        'issues': ['Name truncation: "PRANAY REDDY Sr"', 'Contact parsing']
    }
]

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
        else:
            return "Unsupported format"
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_case(case_info):
    """Analyze a specific failing case"""
    filename = case_info['file']
    file_path = f"/home/great/claudeprojects/parser/test_resumes/Test Resumes/{filename}"

    print(f"\n{'='*60}")
    print(f"🔍 ANALYZING: {filename}")
    print(f"Current Accuracy: {case_info['accuracy']}")
    print(f"Known Issues: {', '.join(case_info['issues'])}")
    print(f"{'='*60}")

    # Extract text
    text = extract_text_from_file(file_path, filename)
    if text.startswith('Error') or text.startswith('Unsupported'):
        print(f"❌ Text extraction failed: {text}")
        return

    print(f"\n📝 TEXT SAMPLE (first 300 chars):")
    print(f"{text[:300]}...")

    # Parse with current parser
    parser = FixedResumeParser()
    result = parser.parse_resume(text, filename)

    # Analyze results
    print(f"\n📊 PARSING RESULTS:")
    contact = result.get('ContactInformation', {})
    name = contact.get('CandidateName', {}).get('FormattedName', 'NOT FOUND')
    email = contact.get('EmailAddresses', [{}])[0].get('Address', 'NOT FOUND') if contact.get('EmailAddresses') else 'NOT FOUND'
    phone = contact.get('Telephones', [{}])[0].get('Raw', 'NOT FOUND') if contact.get('Telephones') else 'NOT FOUND'

    positions = result.get('EmploymentHistory', {}).get('Positions', [])
    skills = result.get('Skills', [])

    print(f"  👤 Name: {name}")
    print(f"  📧 Email: {email}")
    print(f"  📞 Phone: {phone}")
    print(f"  💼 Positions: {len(positions)}")
    print(f"  🛠️  Skills: {len(skills)}")

    # Show positions in detail
    if positions:
        print(f"\n💼 EXPERIENCE DETAILS:")
        for i, pos in enumerate(positions[:3], 1):  # Show first 3
            company = pos.get('Employer', {}).get('Name', 'Unknown')
            title = pos.get('JobTitle', 'Unknown')
            dates = pos.get('Dates', 'Unknown')
            print(f"  {i}. {company} - {title} ({dates})")

    # Identify specific issues
    print(f"\n🚨 IDENTIFIED ISSUES:")
    issues = []

    # Name issues
    if name == 'NOT FOUND' or len(name) < 3:
        issues.append("❌ Name extraction failure")
    elif any(word in name.lower() for word in ['file', 'formats', 'resume', 'document']):
        issues.append("❌ Name contains document artifacts")
    elif name.count(' ') > 4:  # Too many words
        issues.append("❌ Name contains extra text/formatting")

    # Contact issues
    if email == 'NOT FOUND':
        issues.append("❌ Email not found")
    if phone == 'NOT FOUND':
        issues.append("❌ Phone not found")

    # Experience issues
    if len(positions) < 2:
        issues.append(f"❌ Too few positions found ({len(positions)})")
    elif len(positions) > 6:
        issues.append(f"❌ Too many positions found ({len(positions)}) - may include duplicates")

    # Skills issues
    if len(skills) < 5:
        issues.append(f"❌ Too few skills found ({len(skills)})")
    elif len(skills) > 25:
        issues.append(f"❌ Too many skills found ({len(skills)}) - may include noise")

    if issues:
        for issue in issues:
            print(f"  {issue}")
    else:
        print("  ✅ No major structural issues detected")

    return {
        'filename': filename,
        'name': name,
        'email': email,
        'phone': phone,
        'positions_count': len(positions),
        'skills_count': len(skills),
        'issues': issues,
        'text_sample': text[:500]
    }

def main():
    """Main analysis function"""
    print("🔍 COMPREHENSIVE FAILING CASES ANALYSIS")
    print("="*60)

    results = []
    for case in FAILING_CASES:
        try:
            result = analyze_case(case)
            if result:
                results.append(result)
        except Exception as e:
            print(f"❌ Error analyzing {case['file']}: {str(e)}")

    # Summary of common issues
    print(f"\n{'='*60}")
    print("📋 SUMMARY OF COMMON ISSUES")
    print(f"{'='*60}")

    all_issues = []
    for result in results:
        all_issues.extend(result.get('issues', []))

    # Count issue types
    issue_counts = {}
    for issue in all_issues:
        key = issue.split(' ')[1] if len(issue.split(' ')) > 1 else issue
        issue_counts[key] = issue_counts.get(key, 0) + 1

    print("🔥 Most Common Issues:")
    for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {issue}: {count} cases")

    # Save detailed results
    with open('failing_cases_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Detailed analysis saved to: failing_cases_analysis.json")

if __name__ == "__main__":
    main()