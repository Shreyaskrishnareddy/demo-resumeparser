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

echo "✅ Created archive folders"

# Move debug scripts
echo ""
echo "📦 Moving debug scripts..."
mv debug_*.py _archive/debug_scripts/ 2>/dev/null && echo "  ✅ Moved debug_*.py" || echo "  ⚠️  No debug_*.py files"
mv analyze_*.py _archive/debug_scripts/ 2>/dev/null && echo "  ✅ Moved analyze_*.py" || echo "  ⚠️  No analyze_*.py files"
mv examine_*.py _archive/debug_scripts/ 2>/dev/null && echo "  ✅ Moved examine_*.py" || echo "  ⚠️  No examine_*.py files"
mv check_*.py _archive/debug_scripts/ 2>/dev/null && echo "  ✅ Moved check_*.py" || echo "  ⚠️  No check_*.py files"

# Move old parser versions
echo ""
echo "📦 Moving old parser versions..."
mv brd_compliant_parser.py _archive/old_parsers/ 2>/dev/null && echo "  ✅ brd_compliant_parser.py"
mv brd_transformer.py _archive/old_parsers/ 2>/dev/null && echo "  ✅ brd_transformer.py"
mv fast_brd_transformer.py _archive/old_parsers/ 2>/dev/null && echo "  ✅ fast_brd_transformer.py"
mv optimize_brd_transformer.py _archive/old_parsers/ 2>/dev/null && echo "  ✅ optimize_brd_transformer.py"
mv comprehensive_resume_parser.py _archive/old_parsers/ 2>/dev/null && echo "  ✅ comprehensive_resume_parser.py"
mv fixed_resume_parser.py _archive/old_parsers/ 2>/dev/null && echo "  ✅ fixed_resume_parser.py"
mv enterprise_resume_parser.py _archive/old_parsers/ 2>/dev/null && echo "  ✅ enterprise_resume_parser.py"
mv optimized_parser.py _archive/old_parsers/ 2>/dev/null && echo "  ✅ optimized_parser.py"
mv lightning_fast_parser.py _archive/old_parsers/ 2>/dev/null && echo "  ✅ lightning_fast_parser.py"
mv enhanced_real_content_extractor.py _archive/old_parsers/ 2>/dev/null && echo "  ✅ enhanced_real_content_extractor.py"

# Move validators
echo ""
echo "📦 Moving validator scripts..."
mv comprehensive_accuracy_validator.py _archive/validators/ 2>/dev/null && echo "  ✅ comprehensive_accuracy_validator.py"
mv comprehensive_content_validator.py _archive/validators/ 2>/dev/null && echo "  ✅ comprehensive_content_validator.py"
mv comprehensive_field_validation.py _archive/validators/ 2>/dev/null && echo "  ✅ comprehensive_field_validation.py"
mv accuracy_analyzer.py _archive/validators/ 2>/dev/null && echo "  ✅ accuracy_analyzer.py"
mv final_ahmad_validation.py _archive/validators/ 2>/dev/null && echo "  ✅ final_ahmad_validation.py"
mv final_krupakar_validation.py _archive/validators/ 2>/dev/null && echo "  ✅ final_krupakar_validation.py"

# Move test files
echo ""
echo "📦 Moving test files..."
mv comprehensive_parser_comparison.py _archive/test_files/ 2>/dev/null && echo "  ✅ comprehensive_parser_comparison.py"
mv performance_profiler.py _archive/test_files/ 2>/dev/null && echo "  ✅ performance_profiler.py"
mv rigorous_test_suite.py _archive/test_files/ 2>/dev/null && echo "  ✅ rigorous_test_suite.py"
mv ultimate_brd_compliance_test.py _archive/test_files/ 2>/dev/null && echo "  ✅ ultimate_brd_compliance_test.py"
mv comprehensive_verification_test.py _archive/test_files/ 2>/dev/null && echo "  ✅ comprehensive_verification_test.py"
mv test_*.py _archive/test_files/ 2>/dev/null && echo "  ✅ Moved test_*.py" || echo "  ⚠️  No test_*.py files"

# Move old server versions
echo ""
echo "📦 Moving old server versions..."
mv clean_server.py _archive/old_parsers/ 2>/dev/null && echo "  ✅ clean_server.py"
mv lightning_server.py _archive/old_parsers/ 2>/dev/null && echo "  ✅ lightning_server.py"
mv improved_server.py _archive/old_parsers/ 2>/dev/null && echo "  ✅ improved_server.py"

# Move old documentation
echo ""
echo "📦 Moving old documentation..."
mv AHMAD_QASEM_FIXES_SUMMARY.md _archive/old_docs/ 2>/dev/null && echo "  ✅ AHMAD_QASEM_FIXES_SUMMARY.md"
mv AHMAD_QASSEM_RESUME_PARSER_FIXES_SUMMARY.md _archive/old_docs/ 2>/dev/null && echo "  ✅ AHMAD_QASSEM_RESUME_PARSER_FIXES_SUMMARY.md"
mv COMPREHENSIVE_PROJECT_REPORT.md _archive/old_docs/ 2>/dev/null && echo "  ✅ COMPREHENSIVE_PROJECT_REPORT.md"
mv EXECUTIVE_TESTING_REPORT.md _archive/old_docs/ 2>/dev/null && echo "  ✅ EXECUTIVE_TESTING_REPORT.md"
mv FINAL_ISSUES_SUMMARY.md _archive/old_docs/ 2>/dev/null && echo "  ✅ FINAL_ISSUES_SUMMARY.md"
mv FINAL_PARSER_VERIFICATION_RESULTS.md _archive/old_docs/ 2>/dev/null && echo "  ✅ FINAL_PARSER_VERIFICATION_RESULTS.md"
mv FINAL_VALIDATION_REPORT.md _archive/old_docs/ 2>/dev/null && echo "  ✅ FINAL_VALIDATION_REPORT.md"
mv GITHUB_UPDATE_SUMMARY.md _archive/old_docs/ 2>/dev/null && echo "  ✅ GITHUB_UPDATE_SUMMARY.md"
mv PARSER_ISSUES_ANALYSIS_REPORT.md _archive/old_docs/ 2>/dev/null && echo "  ✅ PARSER_ISSUES_ANALYSIS_REPORT.md"
mv RIGOROUS_TESTING_FINAL_REPORT.md _archive/old_docs/ 2>/dev/null && echo "  ✅ RIGOROUS_TESTING_FINAL_REPORT.md"
mv krupakar_comprehensive_analysis_report.md _archive/old_docs/ 2>/dev/null && echo "  ✅ krupakar_comprehensive_analysis_report.md"
mv PROJECT_DELIVERY_REPORT_backup.md _archive/old_docs/ 2>/dev/null && echo "  ✅ PROJECT_DELIVERY_REPORT_backup.md"

# Move utility scripts that are not needed
echo ""
echo "📦 Moving utility scripts..."
mv achievements_extractor.py _archive/old_parsers/ 2>/dev/null && echo "  ✅ achievements_extractor.py"
mv projects_extractor.py _archive/old_parsers/ 2>/dev/null && echo "  ✅ projects_extractor.py"
mv name_parser.py _archive/old_parsers/ 2>/dev/null && echo "  ✅ name_parser.py"
mv current_role_detector.py _archive/old_parsers/ 2>/dev/null && echo "  ✅ current_role_detector.py"
mv job_title_matcher.py _archive/old_parsers/ 2>/dev/null && echo "  ✅ job_title_matcher.py"

echo ""
echo "=================================="
echo "✅ CLEANUP COMPLETE"
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