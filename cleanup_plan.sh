#!/bin/bash

# Safe cleanup script - moves files to _archive instead of deleting
# Run with: bash cleanup_plan.sh

echo "=================================="
echo "SAFE CLEANUP SCRIPT"
echo "=================================="
echo "This will move unused files to _archive/ folder"
echo ""

# Create archive folders
mkdir -p _archive/debug_scripts
mkdir -p _archive/old_parsers
mkdir -p _archive/old_docs
mkdir -p _archive/validators
mkdir -p _archive/test_files

echo "[DONE] Created archive folders"

# Move debug scripts
echo ""
echo "📦 Moving debug scripts..."
mv debug_*.py _archive/debug_scripts/ 2>/dev/null && echo "  [DONE] Moved debug_*.py" || echo "  [WARNING]  No debug_*.py files"
mv analyze_*.py _archive/debug_scripts/ 2>/dev/null && echo "  [DONE] Moved analyze_*.py" || echo "  [WARNING]  No analyze_*.py files"
mv examine_*.py _archive/debug_scripts/ 2>/dev/null && echo "  [DONE] Moved examine_*.py" || echo "  [WARNING]  No examine_*.py files"
mv check_*.py _archive/debug_scripts/ 2>/dev/null && echo "  [DONE] Moved check_*.py" || echo "  [WARNING]  No check_*.py files"

# Move old parser versions
echo ""
echo "📦 Moving old parser versions..."
mv brd_compliant_parser.py _archive/old_parsers/ 2>/dev/null && echo "  [DONE] brd_compliant_parser.py"
mv brd_transformer.py _archive/old_parsers/ 2>/dev/null && echo "  [DONE] brd_transformer.py"
mv fast_brd_transformer.py _archive/old_parsers/ 2>/dev/null && echo "  [DONE] fast_brd_transformer.py"
mv optimize_brd_transformer.py _archive/old_parsers/ 2>/dev/null && echo "  [DONE] optimize_brd_transformer.py"
mv comprehensive_resume_parser.py _archive/old_parsers/ 2>/dev/null && echo "  [DONE] comprehensive_resume_parser.py"
mv fixed_resume_parser.py _archive/old_parsers/ 2>/dev/null && echo "  [DONE] fixed_resume_parser.py"
mv enterprise_resume_parser.py _archive/old_parsers/ 2>/dev/null && echo "  [DONE] enterprise_resume_parser.py"
mv optimized_parser.py _archive/old_parsers/ 2>/dev/null && echo "  [DONE] optimized_parser.py"
mv lightning_fast_parser.py _archive/old_parsers/ 2>/dev/null && echo "  [DONE] lightning_fast_parser.py"
mv enhanced_real_content_extractor.py _archive/old_parsers/ 2>/dev/null && echo "  [DONE] enhanced_real_content_extractor.py"

# Move validators
echo ""
echo "📦 Moving validator scripts..."
mv comprehensive_accuracy_validator.py _archive/validators/ 2>/dev/null && echo "  [DONE] comprehensive_accuracy_validator.py"
mv comprehensive_content_validator.py _archive/validators/ 2>/dev/null && echo "  [DONE] comprehensive_content_validator.py"
mv comprehensive_field_validation.py _archive/validators/ 2>/dev/null && echo "  [DONE] comprehensive_field_validation.py"
mv accuracy_analyzer.py _archive/validators/ 2>/dev/null && echo "  [DONE] accuracy_analyzer.py"
mv final_ahmad_validation.py _archive/validators/ 2>/dev/null && echo "  [DONE] final_ahmad_validation.py"
mv final_krupakar_validation.py _archive/validators/ 2>/dev/null && echo "  [DONE] final_krupakar_validation.py"

# Move test files
echo ""
echo "📦 Moving test files..."
mv comprehensive_parser_comparison.py _archive/test_files/ 2>/dev/null && echo "  [DONE] comprehensive_parser_comparison.py"
mv performance_profiler.py _archive/test_files/ 2>/dev/null && echo "  [DONE] performance_profiler.py"
mv rigorous_test_suite.py _archive/test_files/ 2>/dev/null && echo "  [DONE] rigorous_test_suite.py"
mv ultimate_brd_compliance_test.py _archive/test_files/ 2>/dev/null && echo "  [DONE] ultimate_brd_compliance_test.py"
mv comprehensive_verification_test.py _archive/test_files/ 2>/dev/null && echo "  [DONE] comprehensive_verification_test.py"
mv test_*.py _archive/test_files/ 2>/dev/null && echo "  [DONE] Moved test_*.py" || echo "  [WARNING]  No test_*.py files"

# Move old server versions
echo ""
echo "📦 Moving old server versions..."
mv clean_server.py _archive/old_parsers/ 2>/dev/null && echo "  [DONE] clean_server.py"
mv lightning_server.py _archive/old_parsers/ 2>/dev/null && echo "  [DONE] lightning_server.py"
mv improved_server.py _archive/old_parsers/ 2>/dev/null && echo "  [DONE] improved_server.py"

# Move old documentation
echo ""
echo "📦 Moving old documentation..."
mv AHMAD_QASEM_FIXES_SUMMARY.md _archive/old_docs/ 2>/dev/null && echo "  [DONE] AHMAD_QASEM_FIXES_SUMMARY.md"
mv AHMAD_QASSEM_RESUME_PARSER_FIXES_SUMMARY.md _archive/old_docs/ 2>/dev/null && echo "  [DONE] AHMAD_QASSEM_RESUME_PARSER_FIXES_SUMMARY.md"
mv COMPREHENSIVE_PROJECT_REPORT.md _archive/old_docs/ 2>/dev/null && echo "  [DONE] COMPREHENSIVE_PROJECT_REPORT.md"
mv EXECUTIVE_TESTING_REPORT.md _archive/old_docs/ 2>/dev/null && echo "  [DONE] EXECUTIVE_TESTING_REPORT.md"
mv FINAL_ISSUES_SUMMARY.md _archive/old_docs/ 2>/dev/null && echo "  [DONE] FINAL_ISSUES_SUMMARY.md"
mv FINAL_PARSER_VERIFICATION_RESULTS.md _archive/old_docs/ 2>/dev/null && echo "  [DONE] FINAL_PARSER_VERIFICATION_RESULTS.md"
mv FINAL_VALIDATION_REPORT.md _archive/old_docs/ 2>/dev/null && echo "  [DONE] FINAL_VALIDATION_REPORT.md"
mv GITHUB_UPDATE_SUMMARY.md _archive/old_docs/ 2>/dev/null && echo "  [DONE] GITHUB_UPDATE_SUMMARY.md"
mv PARSER_ISSUES_ANALYSIS_REPORT.md _archive/old_docs/ 2>/dev/null && echo "  [DONE] PARSER_ISSUES_ANALYSIS_REPORT.md"
mv RIGOROUS_TESTING_FINAL_REPORT.md _archive/old_docs/ 2>/dev/null && echo "  [DONE] RIGOROUS_TESTING_FINAL_REPORT.md"
mv krupakar_comprehensive_analysis_report.md _archive/old_docs/ 2>/dev/null && echo "  [DONE] krupakar_comprehensive_analysis_report.md"
mv PROJECT_DELIVERY_REPORT_backup.md _archive/old_docs/ 2>/dev/null && echo "  [DONE] PROJECT_DELIVERY_REPORT_backup.md"

# Move utility scripts that are not needed
echo ""
echo "📦 Moving utility scripts..."
mv achievements_extractor.py _archive/old_parsers/ 2>/dev/null && echo "  [DONE] achievements_extractor.py"
mv projects_extractor.py _archive/old_parsers/ 2>/dev/null && echo "  [DONE] projects_extractor.py"
mv name_parser.py _archive/old_parsers/ 2>/dev/null && echo "  [DONE] name_parser.py"
mv current_role_detector.py _archive/old_parsers/ 2>/dev/null && echo "  [DONE] current_role_detector.py"
mv job_title_matcher.py _archive/old_parsers/ 2>/dev/null && echo "  [DONE] job_title_matcher.py"

echo ""
echo "=================================="
echo "[DONE] CLEANUP COMPLETE"
echo "=================================="
echo ""
echo "Files moved to _archive/ folder"
echo "To restore, move files back from _archive/"
echo "To permanently delete, remove _archive/ folder"
echo ""
echo "Core files kept:"
echo "  - fixed_comprehensive_parser.py (main parser)"
echo "  - comprehensive_validation_report.py (validation)"
echo "  - api_server.py (API server)"
echo "  - production_server.py (production server)"
echo "  - requirements.txt"
echo "  - README.md and key documentation"
echo ""