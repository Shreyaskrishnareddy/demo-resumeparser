from fixed_comprehensive_parser import FixedComprehensiveParser
import traceback

# Debug the parsing error
parser = FixedComprehensiveParser()

try:
    # Parse the resume
    result = parser.parse_resume('Resume&Results/Ahmad Qasem-Resume.pdf')
    print("Parsing succeeded!")
    print(f"Result: {result}")
except Exception as e:
    print("Parsing failed with exception:")
    print(f"Error type: {type(e)}")
    print(f"Error message: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()

# Also test if we can read the PDF directly
print(f"\n=== TESTING PDF READING ===")
try:
    import fitz
    doc = fitz.open('Resume&Results/Ahmad Qasem-Resume.pdf')
    print(f"PDF opened successfully, {len(doc)} pages")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    print(f"Text extracted: {len(text)} characters")
    print(f"First 200 chars: {repr(text[:200])}")
except Exception as e:
    print(f"PDF reading failed: {e}")
    traceback.print_exc()