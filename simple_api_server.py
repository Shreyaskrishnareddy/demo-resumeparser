#!/usr/bin/env python3
"""
Simple Resume Parser API Server with File Upload
Single parser mode that meets BRD requirements
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import traceback

# Import the optimized parser and BRD transformer
from optimized_parser import OptimizedResumeParser
from enterprise_resume_parser import EnterpriseResumeParser
from brd_transformer import BRDTransformer
from fast_brd_transformer import FastBRDTransformer

app = Flask(__name__)

# Initialize parsers
optimized_parser = OptimizedResumeParser()
enterprise_parser = EnterpriseResumeParser()
brd_transformer = BRDTransformer()
fast_brd_transformer = FastBRDTransformer()

# Configuration
UPLOAD_FOLDER = "/home/great/claudeprojects/parser/parserdemo/uploads"
OUTPUT_FOLDER = "/home/great/claudeprojects/parser/parserdemo/output"
SUPPORTED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS

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

def parse_resume_brd_compliant(text_content, filename=""):
    """
    Ultra-fast BRD-compliant parser mode for 2ms target
    Uses optimized fast transformer
    """
    try:
        # Use fast BRD transformer for 2ms performance target
        result = fast_brd_transformer.transform_to_brd_format(text_content, filename)
        return result
    except Exception as e:
        print(f"Fast BRD transformation error: {e}")
        # Fallback to regular BRD transformer if fast one fails
        try:
            result = brd_transformer.transform_to_brd_format(text_content, filename)
            return result
        except Exception as e2:
            print(f"Regular BRD transformation error: {e2}")
            # Final fallback to original parsing
            fallback_result = optimized_parser.parse_resume_fast(text_content)
            return fallback_result

@app.route('/')
def index():
    """Serve the test UI"""
    return send_from_directory('static', 'upload_ui.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Simple Resume Parser API",
        "timestamp": datetime.now().isoformat(),
        "supported_formats": list(SUPPORTED_EXTENSIONS),
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024)
    })

@app.route('/parse', methods=['POST'])
def parse_resume():
    """
    Parse uploaded resume file

    Expects:
    - File upload in 'file' field
    - Optional output_location parameter

    Returns:
    - JSON with parsing results
    - Output file saved to disk
    """
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No file uploaded. Please select a resume file.",
                "timestamp": timestamp
            }), 400

        file = request.files['file']

        # Check if file was selected
        if file.filename == '':
            return jsonify({
                "status": "error",
                "message": "No file selected",
                "timestamp": timestamp
            }), 400

        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                "status": "error",
                "message": f"Unsupported file format. Supported: {list(SUPPORTED_EXTENSIONS)}",
                "timestamp": timestamp
            }), 400

        # Secure filename and save upload
        filename = secure_filename(file.filename)
        timestamp_prefix = datetime.now().strftime("%Y%m%d_%H%M%S_")
        unique_filename = timestamp_prefix + filename
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        # Save uploaded file
        file.save(file_path)

        # Extract text from file
        try:
            text_content = get_file_text(file_path)
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error reading file: {str(e)}",
                "timestamp": timestamp
            }), 500

        # Parse the resume using BRD-compliant mode
        try:
            result = parse_resume_brd_compliant(text_content, filename)

            # Update metadata (BRD transformer already includes metadata)
            if 'ParsingMetadata' not in result:
                result['ParsingMetadata'] = {}

            result['ParsingMetadata']['parser_mode'] = 'brd_compliant'
            result['ParsingMetadata']['processing_time'] = time.time() - start_time
            result['ParsingMetadata']['timestamp'] = timestamp
            result['ParsingMetadata']['source_file'] = unique_filename

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error parsing resume: {str(e)}",
                "timestamp": timestamp,
                "traceback": traceback.format_exc()
            }), 500

        # Generate output filename
        output_filename = f"{Path(filename).stem}_{timestamp_prefix.rstrip('_')}.json"
        output_file_path = os.path.join(OUTPUT_FOLDER, output_filename)

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

        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass

        # Return success response
        processing_time = time.time() - start_time
        return jsonify({
            "status": "success",
            "output_location": output_file_path,
            "timestamp": timestamp,
            "filename": output_filename,
            "processing_time": round(processing_time, 3),
            "message": f"Successfully parsed {filename}",
            "upload_filename": unique_filename,
            "parsed_data": result  # Include parsed data in response
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}",
            "timestamp": timestamp,
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    print("🚀 SIMPLE RESUME PARSER API SERVER")
    print("="*50)
    print("API Endpoints:")
    print("  GET  /health          - Health check")
    print("  POST /parse           - Parse uploaded resume")
    print("="*50)
    print("Server starting on http://localhost:5566")
    print("Upload resume files and get instant JSON results!")
    print("="*50)

    app.run(host='0.0.0.0', port=5566, debug=True)