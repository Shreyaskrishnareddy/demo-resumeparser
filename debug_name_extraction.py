#!/usr/bin/env python3
"""Debug name extraction issues"""

import requests
import json
import sys

def test_specific_file(filename):
    """Test parsing of a specific file to debug name extraction"""

    # Test with production server
    server_url = "http://localhost:8001"

    # Try to get file from uploads directory
    test_files = [
        f"/home/great/claudeprojects/parser/parserdemo/uploads/{filename}",
        f"/home/great/claudeprojects/parser/test_resumes/Test Resumes/{filename}"
    ]

    for test_file in test_files:
        try:
            with open(test_file, 'rb') as f:
                files = {'file': (filename, f, 'application/pdf' if filename.endswith('.pdf') else 'application/msword')}
                response = requests.post(f"{server_url}/api/parse", files=files, timeout=30)

                if response.status_code == 200:
                    result = response.json()

                    print(f"\n=== DEBUGGING {filename} ===")
                    print(f"Server Response:")
                    print(f"  Success: {result.get('success', False)}")

                    if 'ContactInformation' in result:
                        contact = result['ContactInformation']
                        candidate_name = contact.get('CandidateName', {})

                        print(f"\nName Extraction Results:")
                        print(f"  FormattedName: '{candidate_name.get('FormattedName', '')}'")
                        print(f"  GivenName: '{candidate_name.get('GivenName', '')}'")
                        print(f"  FamilyName: '{candidate_name.get('FamilyName', '')}'")

                        if candidate_name.get('FormattedName'):
                            print(f"  ✓ FormattedName populated correctly")
                        else:
                            print(f"  ✗ FormattedName is EMPTY - This is the bug!")

                        # Show email and phone for comparison
                        emails = contact.get('EmailAddresses', [])
                        phones = contact.get('PhoneNumbers', [])

                        print(f"\nOther Contact Info (for comparison):")
                        print(f"  Email: {emails[0].get('EmailAddress', 'None') if emails else 'None'}")
                        print(f"  Phone: {phones[0].get('PhoneNumber', 'None') if phones else 'None'}")

                        return True

        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error testing {test_file}: {e}")
            continue

    print(f"Could not find file: {filename}")
    return False

if __name__ == "__main__":
    # Test the failing files identified in the analysis
    failing_files = [
        "c8bec3dc_PRANAY_REDDY_DE_Resume.pdf",
        "d3bd1d85_PRANAY_REDDY_DE_Resume.pdf"
    ]

    print("Testing name extraction on failing files...")

    for filename in failing_files:
        success = test_specific_file(filename)
        if success:
            break  # Test one successfully

    # Also test a working file for comparison
    print("\n" + "="*50)
    print("Testing a WORKING file for comparison...")
    test_specific_file("91cb2108_Ashok_Kumar.doc")