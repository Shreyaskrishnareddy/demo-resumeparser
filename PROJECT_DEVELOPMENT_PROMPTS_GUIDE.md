# Complete Resume Parser Project - Development Prompts Guide

## Table of Contents
1. [Project Setup & Initial Implementation](#phase-1-project-setup)
2. [Core Parser Development](#phase-2-core-parser-development)
3. [Individual Resume Fixes](#phase-3-individual-resume-fixes)
4. [Comprehensive Testing & Validation](#phase-4-comprehensive-testing)
5. [Field Mapping & BRD Compliance](#phase-5-field-mapping)
6. [Technical Details & Architecture](#technical-details)

---

## Phase 1: Project Setup & Initial Implementation

### Prompt 1.1: Initialize the Project
```
I need to build an enterprise resume parser that can extract structured data from PDF, DOC, DOCX, and TXT files.

Requirements:
- Extract contact information (name, email, phone, location)
- Parse work experience (company, title, dates, description)
- Extract education details (degree, institution, dates)
- Identify skills, certifications, languages
- Extract projects and achievements
- Calculate total experience and domain classification
- Output should be in JSON format
- Must be production-ready with error handling

Create the basic project structure with:
1. A Python parser using python-docx for DOCX, PyMuPDF for PDF
2. A Flask REST API server
3. A simple web UI for file upload
4. Requirements.txt with dependencies

Start with the core parser implementation.
```

**Expected Output:** Basic parser structure with document reading capabilities

---

### Prompt 1.2: Create Server with REST API
```
Create a Flask server that:
1. Serves on localhost:5000
2. Has a /health endpoint for health checks
3. Has a /parse endpoint that accepts multipart/form-data file uploads
4. Returns JSON response with parsed data
5. Includes error handling for invalid files
6. Has a clean HTML UI for file upload with drag-and-drop support
7. Shows processing time and structured results

The UI should display:
- File upload area with drag-and-drop
- Health status indicator
- Parsing results with summary statistics
- Full JSON output in a formatted view
```

**Expected Output:** Working Flask server with upload UI

---

## Phase 2: Core Parser Development

### Prompt 2.1: Implement Contact Information Extraction
```
Enhance the parser to accurately extract personal details:

1. Full name parsing (First, Middle, Last names)
2. Email addresses (support multiple emails)
3. Phone numbers with country code detection
4. Location parsing (city, state, country)
5. Social media links (LinkedIn, GitHub, etc.)

Handle edge cases:
- Names with middle initials
- International phone formats
- Multiple contact methods
- Names in different positions in the resume

Test with various resume formats to ensure robustness.
```

**Expected Output:** Robust contact information extraction

---

### Prompt 2.2: Implement Work Experience Parsing
```
Build comprehensive work experience extraction that:

1. Detects company names accurately
2. Extracts job titles and positions
3. Parses employment dates in multiple formats:
   - YYYY-MM-DD
   - MM YYYY (e.g., "09 2022")
   - Month Year (e.g., "September 2022")
   - "Current", "Till Date", "Present"
4. Calculates experience duration for each position
5. Extracts job descriptions and responsibilities
6. Determines employment type (Full-time, Contract, etc.)
7. Identifies location for each position

Handle special cases:
- Tab-separated dates (e.g., "Company	07/2021	12/2023")
- Overlapping positions
- Current positions without end dates
- Companies with multiple locations

Return experience in chronological order (most recent first).
```

**Expected Output:** Accurate work experience extraction with duration calculation

---

### Prompt 2.3: Implement Education Parsing
```
Create education extraction that handles:

1. Degree types (Bachelor's, Master's, PhD, MBA, etc.)
2. Major/Field of Study
3. University/Institution names
4. Graduation dates and year
5. GPA and honors (if present)
6. Location of institution

Support various formats:
- "Bachelor's in Computer Science - MIT - 2020"
- "Masters in Data Science from Stanford University (2018-2020)"
- "MBA, Harvard Business School, 2015"
- Handle Unicode characters like en-dash (–) and regular dash (-)

Extract multiple education entries and maintain chronological order.
```

**Expected Output:** Multi-format education parsing

---

### Prompt 2.4: Implement Skills, Certifications & Languages
```
Add extraction for:

1. **Skills:**
   - Technical skills (programming languages, frameworks, tools)
   - Soft skills (leadership, communication)
   - Categorize by type
   - Detect experience level and years used
   - Avoid duplicates and generic terms

2. **Certifications:**
   - Full certification names (preserve multi-word names)
   - Issuing authority
   - Issue and expiry dates
   - Certification numbers
   - Handle complex names like "AWS Certified Solutions Architect Associate"
   - Deduplicate similar certifications

3. **Languages:**
   - Language names
   - Proficiency levels (Native, Fluent, Professional, Basic)
   - Reading/Writing/Speaking breakdown

Implement smart filtering to remove:
- Generic words appearing as skills
- Duplicate entries
- Overly broad terms
```

**Expected Output:** Clean skills, certifications, and languages extraction

---

### Prompt 2.5: Implement Projects & Achievements
```
Add extraction for:

1. **Projects:**
   - Project names and titles
   - Descriptions
   - Technologies used
   - Start and end dates
   - Project URLs or links
   - Team size and role

2. **Achievements:**
   - Awards and recognition
   - Quantifiable accomplishments
   - Monetary values (e.g., "$16.2 million project")
   - Performance metrics
   - Publications and patents

Parse from various sections like:
- "Projects"
- "Key Achievements"
- "Accomplishments"
- Inline in work experience descriptions
```

**Expected Output:** Projects and achievements extraction

---

### Prompt 2.6: Implement Summary & Experience Calculation
```
Add intelligent analysis features:

1. **Overall Summary:**
   - Current job role
   - List of relevant job titles held
   - Professional summary text
   - Calculate total years of experience
   - Handle overlapping positions correctly

2. **Experience Calculation:**
   - Sum all work experience durations
   - Handle date format variations
   - Account for overlapping positions (don't double-count)
   - Support "Current" positions up to today's date
   - Format output as "X years Y months"

3. **Domain Classification:**
   - Analyze skills and experience to determine domains
   - Categories: Software Development, Data Science, Project Management, etc.
   - Support multiple domains
   - Primary domain identification

The calculation should be accurate even with:
- MM YYYY format dates
- Missing end dates
- Multiple concurrent positions
```

**Expected Output:** Accurate summary and experience calculation

---

## Phase 3: Individual Resume Fixes

### Prompt 3.1: Fix Specific Resume - Ahmad Qasem
```
I have a resume that's not parsing correctly. Let me provide you with:
1. The original resume file (Ahmad_Qasem-Resume.pdf)
2. The current JSON output
3. Specific issues I'm seeing

Issues found:
- Certifications are being split incorrectly (showing 5 instead of 2)
- Education fields (Major, Institution) are empty
- Total experience shows "12 years" but should be "15 years"
- Current job experience shows "0 months" instead of actual duration
- Date format "MM YYYY" not being parsed

Compare the original content with JSON output and fix all discrepancies.
Think harder about what's wrong and fix each issue one by one.
```

**Expected Actions:**
1. Read both original and parsed content
2. Identify specific parsing failures
3. Fix regex patterns for certifications
4. Add support for Unicode en-dash in education
5. Fix date parsing for MM YYYY format
6. Update experience calculation logic

---

### Prompt 3.2: Fix Specific Resume - Venkat Rohit
```
Same process for Venkat_Rohit resume. Issues found:
- Work experience locations are empty
- Experience durations incorrect
- Skills need better filtering
- Professional Summary being extracted as skills (wrong section)
- Date format: Company names followed by tab-separated dates

Original content shows:
"Visa	09 2022	Till Date"

But parser is not extracting company name or calculating correct duration.

Compare original vs JSON output and fix all issues. Think harder.
```

**Expected Actions:**
1. Fix tab-separated date format parsing
2. Implement location extraction
3. Improve skills vs summary section detection
4. Fix "Till Date" handling

---

### Prompt 3.3: Fix Specific Resume - Krupakar Reddy
```
Krupakar's resume has these issues:
- Only detecting 1 company out of 6 positions
- Work experience deduplication removing valid entries
- Missing education details
- Certifications not found

The resume has positions like:
- Client: NextGen Healthcare
- Client: Chevron
- Company name format includes "Client:" prefix

Fix the parser to handle this format and extract all 6 positions correctly.
```

**Expected Actions:**
1. Handle "Client:" prefix in company names
2. Fix over-aggressive deduplication
3. Improve education section detection
4. Extract certifications from various formats

---

### Prompt 3.4: Fix Specific Resume - Zamen Aladwani
```
Zamen's resume issues:
- Skills being extracted incorrectly (too many generic terms)
- Over-detection of work experience (should be 9 companies, showing 13)
- Need better filtering for valid skills vs noise

The resume has a comprehensive skills section, but parser is extracting:
- Generic words like "Management", "Business", "Operations"
- Duplicate variations of same skill
- Non-technical terms appearing as technical skills

Implement smart filtering to extract only genuine, specific skills.
```

**Expected Actions:**
1. Create skill filtering logic
2. Remove generic business terms
3. Implement deduplication for similar skills
4. Fix work experience over-detection
5. Validate company names before adding

---

## Phase 4: Comprehensive Testing & Validation

### Prompt 4.1: Create Test Framework
```
I have an Excel file "Parser Verification Results.xlsx" with 43 expected fields for 4 resumes.

Create a comprehensive test script that:
1. Parses all 4 resumes
2. Validates each of the 43 fields against expected values
3. Generates a detailed report showing:
   - Total tests: passed/failed
   - Which fields are working vs failing
   - Specific resume + field combinations that fail
   - Success rate percentage
   - Improvement tracking

The 43 fields to test include:
- Personal Details (10 fields): Name, Email, Phone, Location, etc.
- Overall Summary (4 fields): Current Role, Job Titles, Experience, Summary
- Work Experiences (10 fields): Company, Title, Dates, Duration, Type, etc.
- Education (7 fields): Degree, Major, Institution, Year, etc.
- Certifications (2 fields): Name, Issuer
- Languages (2 fields): Name, Proficiency
- Skills, Projects, Achievements, Key Responsibilities, Domain

Run end-to-end test on all resumes and give me a detailed report.
Think harder about validation logic.
```

**Expected Output:** comprehensive_test.py with detailed validation

---

### Prompt 4.2: Analyze Test Results
```
The test results show 114/124 passing (91.9% accuracy) with 10 failures:

Failures:
- Email Address: Missing in all 4 resumes
- Company Name: Missing in Resume 1 & 2
- Work Location: Missing in Resume 1 & 2
- Certification Name/Issuer: Missing in Resume 2

Analyze why these are failing and create a fix plan.
Think harder about root causes.
```

**Expected Analysis:**
1. Field name mismatches (EmailID vs EmailAddress)
2. Missing field aliases in output
3. Section detection issues

---

### Prompt 4.3: Fix All Remaining Issues
```
Let's fix all 10 issues one by one. Think harder.

For each failing test:
1. Identify root cause
2. Implement fix
3. Verify fix works
4. Move to next issue

Issues to fix:
1. Email Address field (all 4 resumes)
2. Company Name field (Resume 1 & 2)
3. Work Location (Resume 1 & 2)
4. Certifications (Resume 2)

Do NOT move to the next issue until current one is completely fixed.
Show me evidence that each fix works before proceeding.
```

**Expected Actions:**
1. Add field aliases: EmailID → EmailAddress, CompanyName → Employer
2. Verify each fix with test output
3. Provide proof of fix before moving forward
4. Final accuracy: 96.8% (122/126 passing)

---

## Phase 5: Field Mapping & BRD Compliance

### Prompt 5.1: Implement BRD-Compliant Output
```
The Business Requirements Document (BRD) specifies exact field names and structure.

Current issues:
- Parser uses "Email" but BRD expects "EmailAddress"
- Parser uses "CompanyName" but BRD expects "Employer"
- Some fields missing from output even though data exists

Solution:
1. Map all field names to BRD-compliant names
2. Add field aliases so both names are present
3. Ensure all 43 required fields are in output (even if empty)
4. Validate output structure matches BRD exactly

Implement field aliases in:
- PersonalDetails section
- ListOfExperiences section
- All other sections

This ensures backward compatibility while meeting BRD requirements.
```

**Expected Output:** BRD-compliant field mapping with aliases

---

### Prompt 5.2: Validate Complete Field Structure
```
Create a validation that ensures output contains all 43 BRD-required fields:

Personal Details (10):
- FullName, FirstName, MiddleName, LastName
- EmailID, EmailAddress, Email (aliases)
- PhoneNumber, CountryCode, Location
- SocialMediaLinks

Overall Summary (4):
- CurrentJobRole
- RelevantJobTitles
- TotalExperience
- Summary

Work Experiences (10):
- CompanyName, Employer (aliases)
- JobTitle, Location, EmploymentType
- StartDate, EndDate
- ExperienceInYears, Summary
- TotalWorkExperience count

Education (7):
- Degree, DegreeType, Major, FieldOfStudy
- Institution, School (aliases)
- GraduationYear, EndDate, Location

... and so on for all 43 fields.

Generate a report confirming all fields are present in output structure.
```

**Expected Output:** Complete field structure validation

---

## Phase 6: Documentation & Deliverables

### Prompt 6.1: Create Comprehensive Documentation
```
Create README.md with:

1. Project overview and features
2. Quick start guide (installation, setup, running)
3. API documentation with examples
4. Architecture overview
5. Performance metrics and accuracy stats
6. Testing instructions
7. Deployment guide (local, Docker, cloud)
8. Security features
9. Contributing guidelines

Make it professional and enterprise-ready.
Include badges for Python version, accuracy, performance, status.
```

**Expected Output:** Professional README.md

---

### Prompt 6.2: Create Validation Reports
```
Generate comprehensive validation reports:

1. **FINAL_VALIDATION_REPORT.md:**
   - Executive summary with accuracy stats
   - Detailed breakdown of improvements
   - Remaining issues (if any)
   - Technical changes made
   - Before/after comparisons

2. **validation_report.json:**
   - Machine-readable test results
   - Total tests, passed, failed
   - Improvement rate
   - Detailed list of improvements and failures

3. **Test result JSON files:**
   - Individual resume parsing results
   - All extracted fields
   - Processing time and metadata

Make reports detailed and suitable for stakeholder review.
```

**Expected Output:** Multiple validation reports


