from fixed_comprehensive_parser import FixedComprehensiveParser
import json
import fitz

# Debug certifications for Ahmad Qasem
parser = FixedComprehensiveParser()

# Read PDF text
doc = fitz.open('Resume&Results/Ahmad Qasem-Resume.pdf')
text = ""
for page in doc:
    text += page.get_text()
doc.close()

# Parse full resume to get certifications
result = parser.parse_resume(text, 'Ahmad Qasem-Resume.pdf')
certifications = result.get('Certifications', [])

print("=== AHMAD QASEM CERTIFICATIONS ANALYSIS ===")
print(f"Total certifications found: {len(certifications)}")
print()

# Analyze each certification
print("=== ALL CERTIFICATIONS ===")
for i, cert in enumerate(certifications, 1):
    if isinstance(cert, dict):
        name = cert.get('Name', cert.get('CertificationName', cert.get('Title', 'N/A')))
        issuer = cert.get('IssuingAuthority', cert.get('Issuer', cert.get('Organization', 'N/A')))
        date = cert.get('DateIssued', cert.get('Date', cert.get('IssueDate', 'N/A')))
        print(f"{i:2d}. Name: {repr(name)}")
        print(f"    Issuer: {repr(issuer)}")
        print(f"    Date: {repr(date)}")
    else:
        print(f"{i:2d}. {repr(cert)}")
    print()

# Look for duplicates and similar entries
print("=== DUPLICATION ANALYSIS ===")

cert_names = []
for cert in certifications:
    if isinstance(cert, dict):
        name = cert.get('Name', cert.get('CertificationName', cert.get('Title', str(cert))))
        cert_names.append(name.strip().lower() if name else '')
    else:
        cert_names.append(str(cert).strip().lower())

# Find exact duplicates
seen = set()
duplicates = []
for i, name in enumerate(cert_names):
    if name in seen and name:
        duplicates.append((i+1, name))
    seen.add(name)

if duplicates:
    print(f"EXACT DUPLICATES ({len(duplicates)}):")
    for cert_num, name in duplicates:
        print(f"  #{cert_num}: '{name}'")

# Find similar certifications (PMP related, etc.)
print(f"\n=== SIMILAR CERTIFICATION GROUPS ===")

# Group PMP-related certifications
pmp_related = []
for i, name in enumerate(cert_names):
    if 'pmp' in name or 'project management professional' in name:
        pmp_related.append((i+1, name))

if pmp_related:
    print(f"PMP RELATED ({len(pmp_related)}):")
    for cert_num, name in pmp_related:
        print(f"  #{cert_num}: '{name}'")

# Group Scrum/Agile related
scrum_related = []
for i, name in enumerate(cert_names):
    if any(word in name for word in ['scrum', 'agile', 'master', 'csm']):
        scrum_related.append((i+1, name))

if scrum_related:
    print(f"SCRUM/AGILE RELATED ({len(scrum_related)}):")
    for cert_num, name in scrum_related:
        print(f"  #{cert_num}: '{name}'")

# Group Microsoft related
microsoft_related = []
for i, name in enumerate(cert_names):
    if 'microsoft' in name or 'ms office' in name or 'excel' in name:
        microsoft_related.append((i+1, name))

if microsoft_related:
    print(f"MICROSOFT RELATED ({len(microsoft_related)}):")
    for cert_num, name in microsoft_related:
        print(f"  #{cert_num}: '{name}'")