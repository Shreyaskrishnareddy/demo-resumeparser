from docx import Document

# Debug section detection
doc = Document('Resume&Results/KrupakarReddy_SystemP.docx')
text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])

lines = text.split('\n')
print('=== SECTION DETECTION DETAILED DEBUG ===')

for i, line in enumerate(lines):
    line_upper = line.strip().upper().rstrip(':')
    
    # Test exact conditions from parser
    cond1 = line_upper in ['EMPLOYMENT HISTORY', 'WORK EXPERIENCE', 'PROFESSIONAL EXPERIENCE', 'CAREER HISTORY', 'EMPLOYMENT', 'WORK HISTORY', 'EXPERIENCE DETAILS']
    cond2 = (line_upper == 'EXPERIENCE' and len(line.strip().split()) == 1)
    
    if cond1 or cond2:
        print(f'Line {i}: "{line.strip()}"')
        print(f'  line_upper: "{line_upper}"')
        print(f'  word count: {len(line.strip().split())}')
        print(f'  condition 1 (in list): {cond1}')
        print(f'  condition 2 (single EXPERIENCE): {cond2}')
        print(f'  WOULD MATCH: {cond1 or cond2}')
        if cond1 or cond2:
            print(f'  -> Parser would start at line {i+1}')
        print()
