#!/usr/bin/env python3
"""
Resume Parser API Server
Provides structured API endpoints for parsing resumes with configurable input/output locations
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import traceback

# Import the optimized parser
from optimized_parser import OptimizedResumeParser
from enterprise_resume_parser import EnterpriseResumeParser

app = Flask(__name__)

# Initialize parsers
optimized_parser = OptimizedResumeParser()
enterprise_parser = EnterpriseResumeParser()

# Configuration
DEFAULT_OUTPUT_DIR = "/home/great/claudeprojects/parser/parserdemo/output"
SUPPORTED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt'}

def ensure_directory_exists(directory):
    """Create directory if it doesn't exist"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def get_file_text(file_path):
    """Extract text from various file formats"""
    import fitz  # PyMuPDF for PDFs
    from docx import Document

    file_path = Path(file_path)
    extension = file_path.suffix.lower()

    try:
        if extension == '.pdf':
            doc = fitz.open(str(file_path))
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text

        elif extension == '.docx':
            doc = Document(str(file_path))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text

        elif extension == '.doc':
            # For .doc files, try to read as text (basic support)
            try:
                with open(file_path, 'rb') as f:
                    import subprocess
                    result = subprocess.run(['antiword', str(file_path)],
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return result.stdout
            except:
                pass
            # Fallback: read as binary and extract readable text
            with open(file_path, 'rb') as f:
                content = f.read()
                text = ''.join(chr(byte) for byte in content if 32 <= byte <= 126)
                return text

        elif extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

        else:
            raise ValueError(f"Unsupported file format: {extension}")

    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {str(e)}")

@app.route('/')
def index():
    """Serve the test UI"""
    return send_from_directory('static', 'test_ui.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Resume Parser API",
        "timestamp": datetime.now().isoformat(),
        "supported_formats": list(SUPPORTED_EXTENSIONS)
    })

@app.route('/parse', methods=['POST'])
def parse_resume():
    """
    Main API endpoint for parsing resumes

    Request JSON:
    {
        "input_source": "/path/to/input/directory/or/file",
        "parse_quantity": "S" (Single) or "B" (Bulk) - default "S",
        "filename": "resume.pdf" (required if Single),
        "format": ".pdf" (file extension),
        "output_location": "/path/to/output/directory" (optional),
        "parser_mode": "fast" | "balanced" | "full" (optional, default "balanced")
    }

    Response JSON:
    {
        "status": "success" | "error",
        "output_location": "/path/to/output/file.json",
        "timestamp": "2024-09-19T15:30:45",
        "filename": "resume.json",
        "processing_time": 1.23,
        "message": "Success message or error details"
    }
    """

    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    try:
        # Parse request JSON
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "Invalid JSON request body",
                "timestamp": timestamp
            }), 400

        # Extract parameters
        input_source = data.get('input_source')
        parse_quantity = data.get('parse_quantity', 'S').upper()
        filename = data.get('filename')
        file_format = data.get('format', '').lower()
        output_location = data.get('output_location', DEFAULT_OUTPUT_DIR)
        parser_mode = data.get('parser_mode', 'balanced').lower()

        # Validation
        if not input_source:
            return jsonify({
                "status": "error",
                "message": "input_source is required",
                "timestamp": timestamp
            }), 400

        if parse_quantity == 'S' and not filename:
            return jsonify({
                "status": "error",
                "message": "filename is required for single file parsing",
                "timestamp": timestamp
            }), 400

        if file_format and file_format not in SUPPORTED_EXTENSIONS:
            return jsonify({
                "status": "error",
                "message": f"Unsupported format: {file_format}. Supported: {list(SUPPORTED_EXTENSIONS)}",
                "timestamp": timestamp
            }), 400

        # Ensure output directory exists
        ensure_directory_exists(output_location)

        # Handle single file parsing
        if parse_quantity == 'S':
            # Construct full input file path
            input_path = Path(input_source)
            if input_path.is_file():
                file_path = input_path
            else:
                file_path = input_path / filename

            if not file_path.exists():
                return jsonify({
                    "status": "error",
                    "message": f"File not found: {file_path}",
                    "timestamp": timestamp
                }), 404

            # Validate file extension
            actual_format = file_path.suffix.lower()
            if file_format and actual_format != file_format:
                return jsonify({
                    "status": "error",
                    "message": f"File format mismatch. Expected: {file_format}, Found: {actual_format}",
                    "timestamp": timestamp
                }), 400

            if actual_format not in SUPPORTED_EXTENSIONS:
                return jsonify({
                    "status": "error",
                    "message": f"Unsupported file format: {actual_format}",
                    "timestamp": timestamp
                }), 400

            # Extract text from file
            try:
                text_content = get_file_text(file_path)
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": f"Error reading file: {str(e)}",
                    "timestamp": timestamp
                }), 500

            # Parse the resume
            try:
                if parser_mode == 'fast':
                    result = optimized_parser.parse_resume_fast(text_content)
                elif parser_mode == 'full':
                    result = enterprise_parser.parse_resume(text_content, str(file_path))
                else:  # balanced
                    # Use optimized parser with enterprise enhancements
                    result = optimized_parser.parse_resume_fast(text_content)

                    # Add enterprise enhancements for substantial resumes
                    if len(text_content) > 500:
                        try:
                            enterprise_skills = enterprise_parser._extract_skills_enhanced(text_content)
                            if len(enterprise_skills) > len(result['Skills']):
                                result['Skills'] = enterprise_skills

                            domain_classification = enterprise_parser._extract_domain_classification(text_content, result['Skills'])
                            result['DomainClassification'] = domain_classification

                            if len(text_content) > 1000:
                                achievements = enterprise_parser._extract_achievements_enhanced(text_content)
                                result['Achievements'] = achievements
                        except:
                            pass

                # Add metadata
                result['parser_mode'] = parser_mode
                result['processing_time'] = time.time() - start_time
                result['timestamp'] = timestamp
                result['source_file'] = str(file_path)

            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": f"Error parsing resume: {str(e)}",
                    "timestamp": timestamp,
                    "traceback": traceback.format_exc()
                }), 500

            # Generate output filename
            output_filename = f"{file_path.stem}.json"
            output_file_path = Path(output_location) / output_filename

            # Save result to JSON file
            try:
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": f"Error saving output file: {str(e)}",
                    "timestamp": timestamp
                }), 500

            # Return success response
            processing_time = time.time() - start_time
            return jsonify({
                "status": "success",
                "output_location": str(output_file_path),
                "timestamp": timestamp,
                "filename": output_filename,
                "processing_time": round(processing_time, 3),
                "message": f"Successfully parsed {filename} using {parser_mode} mode",
                "parser_mode": parser_mode,
                "input_file": str(file_path)
            })

        else:  # Bulk processing
            return jsonify({
                "status": "error",
                "message": "Bulk processing not yet implemented",
                "timestamp": timestamp
            }), 501

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}",
            "timestamp": timestamp,
            "traceback": traceback.format_exc()
        }), 500

@app.route('/list-files', methods=['POST'])
def list_files():
    """
    List files in a directory for browsing

    Request JSON:
    {
        "directory": "/path/to/directory",
        "filter_extensions": [".pdf", ".docx", ".doc"] (optional)
    }
    """
    try:
        data = request.get_json()
        directory = data.get('directory')
        filter_extensions = data.get('filter_extensions', list(SUPPORTED_EXTENSIONS))

        if not directory:
            return jsonify({
                "status": "error",
                "message": "directory parameter is required"
            }), 400

        dir_path = Path(directory)
        if not dir_path.exists():
            return jsonify({
                "status": "error",
                "message": f"Directory not found: {directory}"
            }), 404

        if not dir_path.is_dir():
            return jsonify({
                "status": "error",
                "message": f"Path is not a directory: {directory}"
            }), 400

        # List files with supported extensions
        files = []
        for file_path in dir_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in filter_extensions:
                files.append({
                    "name": file_path.name,
                    "extension": file_path.suffix.lower(),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })

        return jsonify({
            "status": "success",
            "directory": str(dir_path),
            "files": sorted(files, key=lambda x: x['name']),
            "count": len(files),
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error listing files: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("🚀 RESUME PARSER API SERVER")
    print("="*50)
    print("API Endpoints:")
    print("  GET  /health          - Health check")
    print("  POST /parse           - Parse resume(s)")
    print("  POST /list-files      - List files in directory")
    print("="*50)
    print("Server starting on http://localhost:5555")
    print("Use Postman or curl to test the API")
    print("="*50)

    # Ensure default output directory exists
    ensure_directory_exists(DEFAULT_OUTPUT_DIR)

    app.run(host='0.0.0.0', port=5555, debug=True)