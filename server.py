#!/usr/bin/env python3
"""
Resume Parser Deployment Server
Lightweight Flask server for production deployment
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import time
import uuid
import logging
from pathlib import Path
from fixed_comprehensive_parser import FixedComprehensiveParser
import fitz  # PyMuPDF
from docx import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize parser
parser = FixedComprehensiveParser()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_transaction_id():
    return str(uuid.uuid4())[:8]

def extract_text_from_file(file_path):
    """Extract text from PDF or DOCX file"""
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
        elif extension in ['.docx', '.doc']:
            doc = Document(str(file_path))
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            return text
        elif extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return None
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        return None

@app.route('/')
def index():
    """Homepage with API documentation"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Resume Parser API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #333; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { color: #0066cc; font-weight: bold; }
            code { background: #e0e0e0; padding: 2px 6px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>Resume Parser API</h1>
        <p>Professional resume parsing service extracting 43 structured fields</p>

        <div class="endpoint">
            <p><span class="method">GET</span> <code>/api/health</code></p>
            <p>Health check endpoint</p>
        </div>

        <div class="endpoint">
            <p><span class="method">POST</span> <code>/api/parse</code></p>
            <p>Parse a resume file</p>
            <p><strong>Parameters:</strong></p>
            <ul>
                <li><code>file</code> - Resume file (PDF, DOCX, TXT)</li>
            </ul>
        </div>

        <div class="endpoint">
            <p><strong>Field Coverage:</strong> 43 fields including:</p>
            <ul>
                <li>Personal Details (8 fields)</li>
                <li>Work Experience (8 fields)</li>
                <li>Skills (4 fields)</li>
                <li>Education (6 fields)</li>
                <li>Certifications (3 fields)</li>
                <li>Projects (6 fields)</li>
                <li>And more...</li>
            </ul>
        </div>
    </body>
    </html>
    ''')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'resume-parser',
        'version': '2.0',
        'timestamp': time.time()
    })

@app.route('/api/parse', methods=['POST'])
def parse_resume():
    """Parse resume endpoint"""
    start_time = time.time()
    transaction_id = generate_transaction_id()

    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided',
                'transaction_id': transaction_id
            }), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'transaction_id': transaction_id
            }), 400

        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'File type not allowed. Supported: PDF, DOCX, TXT',
                'transaction_id': transaction_id
            }), 400

        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, f"{transaction_id}_{filename}")
        file.save(filepath)

        # Extract text
        text = extract_text_from_file(filepath)

        if not text:
            return jsonify({
                'success': False,
                'error': 'Could not extract text from file',
                'transaction_id': transaction_id
            }), 400

        # Parse resume
        result = parser.parse_resume(text, filename)

        # Clean up file
        try:
            os.remove(filepath)
        except:
            pass

        processing_time = time.time() - start_time

        return jsonify({
            'success': True,
            'transaction_id': transaction_id,
            'processing_time_ms': round(processing_time * 1000, 2),
            'data': result
        })

    except Exception as e:
        logger.error(f"Error parsing resume: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'transaction_id': transaction_id
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)