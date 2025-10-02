import sys
sys.path.insert(0, '.')

# Force reload
if 'fixed_comprehensive_parser' in sys.modules:
    del sys.modules['fixed_comprehensive_parser']

from fixed_comprehensive_parser import FixedComprehensiveParser
import fitz

# Load resume
doc = fitz.open('Resume&Results/Ahmad Qasem-Resume.pdf')
text = ""
for page in doc:
    text += page.get_text()
doc.close()

# Parse
parser = FixedComprehensiveParser()
result = parser.parse_resume(text, 'Ahmad_Qasem-Resume.pdf')

# Check specific issues
print("\n🔍 DIRECT PARSER TEST RESULTS:")
print("="*60)
print(f"✅ Skills Count: {len(result['ListOfSkills'])}")
print(f"✅ Achievements: {result['Achievements'][0]['Description'][:100] if result['Achievements'] else 'None'}")
print(f"✅ Projects Count: {len(result['Projects'])}")

ligadata = [e for e in result['ListOfExperiences'] if 'Ligadata' in e['CompanyName']]
if ligadata:
    summary = ligadata[0]['Summary']
    has_email = '@' in summary[:200]
    print(f"✅ Ligadata has email: {has_email}")
    if has_email:
        print(f"   First 150 chars: {summary[:150]}")

print(f"✅ KeyResponsibilities Count: {len(result['KeyResponsibilities'])}")
if result['KeyResponsibilities']:
    print(f"   First: {result['KeyResponsibilities'][0][:100]}")
