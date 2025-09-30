from fixed_comprehensive_parser import FixedComprehensiveParser
import fitz

# Check the exact Unicode characters in the degree field
parser = FixedComprehensiveParser()

# Read PDF text
doc = fitz.open('Resume&Results/Ahmad Qasem-Resume.pdf')
text = ""
for page in doc:
    text += page.get_text()
doc.close()

result = parser.parse_resume(text, 'Ahmad Qasem-Resume.pdf')
education = result.get('Education', [])

if education:
    degree = education[0].get('Degree', '')
    print(f"Degree: {repr(degree)}")
    print(f"Degree bytes: {degree.encode('utf-8')}")
    print(f"Character analysis:")
    for i, char in enumerate(degree):
        print(f"  {i:2d}: '{char}' (ord {ord(char)})")
        if char in ["'", "'"]:
            print(f"      ^ This is {'ASCII apostrophe' if ord(char) == 39 else 'Unicode smart quote'}")

    # Test with Unicode-aware comparison
    expected_with_unicode = "Bachelor's Degree of Computer Engineering"
    expected_with_ascii = "Bachelor's Degree of Computer Engineering"

    print(f"\nComparison tests:")
    print(f"Matches Unicode apostrophe: {degree == expected_with_unicode}")
    print(f"Matches ASCII apostrophe: {degree == expected_with_ascii}")

    # Try normalizing
    import unicodedata
    degree_normalized = unicodedata.normalize('NFKC', degree)
    print(f"Normalized degree: {repr(degree_normalized)}")
    print(f"Matches after normalization: {degree_normalized == expected_with_ascii}")