#!/usr/bin/env python3
"""
CSV Bulk Resume Processor
Handles bulk processing of 50+ resumes from CSV input as per BRD requirements
"""

import os
import csv
import json
import logging
import asyncio
import concurrent.futures
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
from pathlib import Path

from enterprise_resume_parser import EnterpriseResumeParser
from image_resume_processor import ImageResumeProcessor

logger = logging.getLogger(__name__)

class CSVBulkProcessor:
    def __init__(self, max_workers: int = 10):
        """Initialize bulk processor with configurable concurrency"""
        self.max_workers = max_workers
        self.parser = EnterpriseResumeParser()
        self.image_processor = ImageResumeProcessor()

        # Processing statistics
        self.stats = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': None,
            'end_time': None
        }

        logger.info(f"📦 CSV Bulk Processor initialized with {max_workers} workers")

    def process_csv_batch(self, csv_file_path: str, resume_folder: str, output_file: str = None) -> Dict[str, Any]:
        """
        Process a batch of resumes from CSV file

        Args:
            csv_file_path: Path to CSV file containing resume metadata
            resume_folder: Folder containing resume files
            output_file: Optional output file for results

        CSV Format Expected:
        - file_name: Resume file name
        - candidate_id: Optional candidate identifier
        - source: Optional source (e.g., job board)
        - priority: Optional priority level (high, medium, low)

        Returns:
            Dictionary with processing results and statistics
        """
        self.stats['start_time'] = datetime.now()
        logger.info(f"🚀 Starting bulk processing from CSV: {csv_file_path}")

        try:
            # Load CSV data
            resume_list = self._load_csv_file(csv_file_path)

            if not resume_list:
                return {
                    'success': False,
                    'error': 'No valid resume entries found in CSV',
                    'stats': self.stats
                }

            # Validate resume files exist
            validated_list = self._validate_resume_files(resume_list, resume_folder)

            self.stats['total_files'] = len(validated_list)
            logger.info(f"📊 Processing {self.stats['total_files']} resumes")

            # Process resumes in parallel
            results = self._process_resumes_parallel(validated_list)

            # Generate output
            output_data = {
                'processing_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'csv_file': csv_file_path,
                    'resume_folder': resume_folder,
                    'total_processed': len(results),
                    'statistics': self.stats
                },
                'results': results
            }

            # Save results if output file specified
            if output_file:
                self._save_results(output_data, output_file)

            self.stats['end_time'] = datetime.now()
            processing_time = (self.stats['end_time'] - self.stats['start_time']).total_seconds()

            logger.info(f"✅ Bulk processing completed in {processing_time:.2f}s")
            logger.info(f"📈 Success: {self.stats['successful']}, Failed: {self.stats['failed']}, Skipped: {self.stats['skipped']}")

            return {
                'success': True,
                'results': results,
                'stats': self.stats,
                'processing_time_seconds': processing_time,
                'output_file': output_file
            }

        except Exception as e:
            logger.error(f"Bulk processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats
            }

    def _load_csv_file(self, csv_file_path: str) -> List[Dict]:
        """Load and validate CSV file"""
        try:
            df = pd.read_csv(csv_file_path)

            # Required column validation
            required_columns = ['file_name']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            # Convert to list of dictionaries
            resume_list = df.to_dict('records')

            logger.info(f"📄 Loaded {len(resume_list)} entries from CSV")
            return resume_list

        except Exception as e:
            logger.error(f"Failed to load CSV file: {e}")
            raise

    def _validate_resume_files(self, resume_list: List[Dict], resume_folder: str) -> List[Dict]:
        """Validate that resume files exist and add full paths"""
        validated_list = []

        for entry in resume_list:
            file_name = entry.get('file_name', '').strip()
            if not file_name:
                logger.warning("Empty file_name in CSV entry, skipping")
                self.stats['skipped'] += 1
                continue

            full_path = os.path.join(resume_folder, file_name)

            if os.path.exists(full_path):
                entry['full_path'] = full_path
                entry['file_size'] = os.path.getsize(full_path)
                validated_list.append(entry)
            else:
                logger.warning(f"File not found: {file_name}")
                self.stats['skipped'] += 1

        logger.info(f"✅ Validated {len(validated_list)} resume files")
        return validated_list

    def _process_resumes_parallel(self, resume_list: List[Dict]) -> List[Dict]:
        """Process resumes in parallel using ThreadPoolExecutor"""
        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_resume = {
                executor.submit(self._process_single_resume, resume_data): resume_data
                for resume_data in resume_list
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_resume):
                resume_data = future_to_resume[future]

                try:
                    result = future.result()
                    results.append(result)

                    if result['success']:
                        self.stats['successful'] += 1
                    else:
                        self.stats['failed'] += 1

                    # Log progress
                    processed = len(results)
                    if processed % 10 == 0:
                        logger.info(f"📊 Processed {processed}/{len(resume_list)} resumes")

                except Exception as e:
                    logger.error(f"Processing failed for {resume_data.get('file_name', 'unknown')}: {e}")
                    self.stats['failed'] += 1

                    results.append({
                        'success': False,
                        'file_name': resume_data.get('file_name', 'unknown'),
                        'error': str(e),
                        'metadata': resume_data
                    })

        return results

    def _process_single_resume(self, resume_data: Dict) -> Dict:
        """Process a single resume file"""
        file_path = resume_data['full_path']
        file_name = resume_data['file_name']

        try:
            # Extract text based on file type
            text = self._extract_text_from_file(file_path, file_name)

            if not text or len(text.strip()) < 50:
                return {
                    'success': False,
                    'file_name': file_name,
                    'error': 'Insufficient text extracted',
                    'metadata': resume_data
                }

            # Parse the resume
            start_time = datetime.now()
            parsed_result = self.parser.parse_resume(text)
            processing_time = (datetime.now() - start_time).total_seconds()

            # Add metadata
            parsed_result['processing_metadata'] = {
                'file_name': file_name,
                'file_size': resume_data.get('file_size', 0),
                'candidate_id': resume_data.get('candidate_id', ''),
                'source': resume_data.get('source', ''),
                'priority': resume_data.get('priority', 'medium'),
                'processing_time_ms': round(processing_time * 1000, 2),
                'text_length': len(text)
            }

            return {
                'success': True,
                'file_name': file_name,
                'parsed_data': parsed_result,
                'metadata': resume_data
            }

        except Exception as e:
            logger.error(f"Failed to process {file_name}: {e}")
            return {
                'success': False,
                'file_name': file_name,
                'error': str(e),
                'metadata': resume_data
            }

    def _extract_text_from_file(self, file_path: str, filename: str) -> str:
        """Extract text from various file formats"""
        try:
            # Check if it's an image file
            if self.image_processor.is_image_file(filename):
                result = self.image_processor.process_image_resume(file_path)
                if result['success']:
                    return result['extracted_text']
                else:
                    raise Exception(f"OCR failed: {result.get('error', 'Unknown error')}")

            # Handle other file types (PDF, DOC, etc.)
            import mimetypes
            import fitz  # PyMuPDF
            from docx import Document
            import docx2txt

            mime_type, _ = mimetypes.guess_type(filename)

            if filename.lower().endswith('.pdf') or mime_type == 'application/pdf':
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text

            elif filename.lower().endswith(('.docx', '.doc')):
                try:
                    doc = Document(file_path)
                    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                    if text.strip():
                        return text
                except Exception:
                    pass

                try:
                    text = docx2txt.process(file_path)
                    if text.strip():
                        return text
                except Exception:
                    pass

            elif filename.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()

            else:
                # Try as text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()

        except Exception as e:
            logger.error(f"Text extraction failed for {filename}: {e}")
            return ""

    def _save_results(self, output_data: Dict, output_file: str):
        """Save processing results to file"""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Save as JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"💾 Results saved to: {output_file}")

            # Also create a summary CSV
            summary_file = output_file.replace('.json', '_summary.csv')
            self._create_summary_csv(output_data, summary_file)

        except Exception as e:
            logger.error(f"Failed to save results: {e}")

    def _create_summary_csv(self, output_data: Dict, summary_file: str):
        """Create a summary CSV file"""
        try:
            summary_data = []

            for result in output_data['results']:
                row = {
                    'file_name': result['file_name'],
                    'success': result['success'],
                    'candidate_id': result.get('metadata', {}).get('candidate_id', ''),
                    'source': result.get('metadata', {}).get('source', ''),
                    'priority': result.get('metadata', {}).get('priority', ''),
                }

                if result['success']:
                    parsed_data = result.get('parsed_data', {})
                    contact_info = parsed_data.get('ContactInformation', {})

                    row.update({
                        'full_name': contact_info.get('FullName', ''),
                        'email': contact_info.get('EmailAddresses', [{}])[0].get('EmailAddress', '') if contact_info.get('EmailAddresses') else '',
                        'phone': contact_info.get('PhoneNumbers', [{}])[0].get('Raw', '') if contact_info.get('PhoneNumbers') else '',
                        'experience_years': parsed_data.get('QualificationsSummary', {}).get('YearsOfExperience', ''),
                        'skills_count': len(parsed_data.get('Skills', [])),
                        'education_count': len(parsed_data.get('Education', [])),
                        'error': ''
                    })
                else:
                    row.update({
                        'full_name': '',
                        'email': '',
                        'phone': '',
                        'experience_years': '',
                        'skills_count': 0,
                        'education_count': 0,
                        'error': result.get('error', 'Unknown error')
                    })

                summary_data.append(row)

            # Save summary CSV
            df = pd.DataFrame(summary_data)
            df.to_csv(summary_file, index=False)

            logger.info(f"📊 Summary CSV saved to: {summary_file}")

        except Exception as e:
            logger.error(f"Failed to create summary CSV: {e}")

    def create_sample_csv(self, output_path: str, resume_files: List[str] = None):
        """Create a sample CSV file for bulk processing"""
        try:
            if not resume_files:
                resume_files = [
                    'resume1.pdf', 'resume2.docx', 'resume3.jpg', 'resume4.pdf', 'resume5.doc'
                ]

            sample_data = []
            for i, file_name in enumerate(resume_files):
                sample_data.append({
                    'file_name': file_name,
                    'candidate_id': f'CAND_{i+1:03d}',
                    'source': 'job_board' if i % 2 == 0 else 'referral',
                    'priority': 'high' if i % 3 == 0 else 'medium'
                })

            df = pd.DataFrame(sample_data)
            df.to_csv(output_path, index=False)

            logger.info(f"📝 Sample CSV created at: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to create sample CSV: {e}")
            return False

# Test the bulk processor
if __name__ == "__main__":
    processor = CSVBulkProcessor(max_workers=5)

    print("📦 CSV Bulk Resume Processor Test")
    print("=" * 50)

    # Create sample CSV
    sample_csv = "sample_resumes.csv"
    processor.create_sample_csv(sample_csv)
    print(f"✅ Sample CSV created: {sample_csv}")

    # Test processing (with sample data)
    resume_folder = "sample_resumes"  # Would contain actual resume files
    output_file = f"bulk_processing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    print(f"\n🧪 Test Configuration:")
    print(f"   CSV File: {sample_csv}")
    print(f"   Resume Folder: {resume_folder}")
    print(f"   Output File: {output_file}")
    print(f"   Max Workers: {processor.max_workers}")

    # Note: Actual processing would require the resume folder to exist
    print(f"\n📋 To run actual bulk processing:")
    print(f"   1. Create folder: {resume_folder}")
    print(f"   2. Add resume files matching CSV entries")
    print(f"   3. Run: processor.process_csv_batch('{sample_csv}', '{resume_folder}', '{output_file}')")

    print(f"\n✅ Bulk processor ready for enterprise-scale processing!")